# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 16:54:02 2014
@author: apple
"""

import PIL
from PIL import Image
import os
from pylab import *
from numpy import *
from scipy import *
from scipy.ndimage import filters
from scipy.ndimage import measurements,morphology
import scipy.misc
import urllib, urlparse
import simplejson as json
import sift
import pydot

#from numpy import *
#from scipy import linalg



fileName = '/Users/apple/Documents/set_free.png'


import pgmagick as pg


def trans_mask_sobel(img):
    """ Generate a transparency mask for a given image """

    image = pg.Image(img)

    # Find object
    image.negate()
    image.edge()
    image.blur(1)
    image.threshold(24)
    image.adaptiveThreshold(5, 5, 5)

    # Fill background
    image.fillColor('magenta')
    w, h = image.size().width(), image.size().height()
    image.floodFillColor('0x0', 'magenta')
    image.floodFillColor('0x0+%s+0' % (w-1), 'magenta')
    image.floodFillColor('0x0+0+%s' % (h-1), 'magenta')
    image.floodFillColor('0x0+%s+%s' % (w-1, h-1), 'magenta')

    image.transparent('magenta')
    return image

def alpha_composite(image, mask):
    """ Composite two images together by overriding one opacity channel """

    compos = pg.Image(mask)
    compos.composite(
        image,
        image.size(),
        pg.CompositeOperator.CopyOpacityCompositeOp
    )
    return compos

def remove_background(filename):
    """ Remove the background of the image in 'filename' """

    img = pg.Image(filename)
    transmask = trans_mask_sobel(img)
    img = alphacomposite(transmask, img)
    img.trim()
    img.write('out.png')

class Camera(object):
    """ Class for representing pin-hole cameras. """
    def __init__(self,P):
        """ Initialize P = K[R|t] camera model. """
        self.P = P
        self.K = None # calibration matrix
        self.R = None # rotation
        self.t = None # translation
        self.c = None # camera center
    def project(self,X):
        """ Project points in X (4*n array) and normalize coordinates. """
        x = dot(self.P,X)
        for i in range(3):
            x[i] /= x[2]
        return x
#The example below
    def rotation_matrix(a):
        """ Creates a 3D rotation matrix for rotation
        around the axis of the vector a. """
        R = eye(4)
        R[:3,:3] = linalg.expm([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
        return R
    def factor(self):
        """ Factorize the camera matrix into K,R,t as P = K[R|t]. """
        # factor first 3*3 part
        K,R = linalg.rq(self.P[:,:3])
        T = diag(sign(diag(K)))
        if linalg.det(T) < 0:
            T[1,1] *= -1
        self.K = dot(K,T)
        self.R = dot(T,R) # T is its own inverse
        self.t = dot(linalg.inv(self.K),self.P[:,3])
        return self.K, self.R, self.t



def appendPath(path, filename):
    return os.path.join(path,filename)

def compute_rigid_transform(refpoints,points):
    """ Computes rotation, scale and translation for
    aligning points to refpoints. """
    A = array([[points[0], -points[1], 1, 0],
                [points[1], points[0], 0, 1],
                [points[2], -points[3], 1, 0],
                [points[3], points[2], 0, 1],
                [points[4], -points[5], 1, 0],
                [points[5], points[4], 0, 1]])
    y = array([ refpoints[0],
                refpoints[1],
                refpoints[2],
                refpoints[3],
                refpoints[4],
                refpoints[5]])
                # least sq solution to mimimize ||Ax - y||
    a,b,tx,ty = linalg.lstsq(A,y)[0]
    R = array([[a, -b], [b, a]]) # rotation matrix incl scale
    return R,tx,ty

def dotDemo():
    g = pydot.Dot(graph_type='graph')
    g.add_node(pydot.Node(str(0),fontcolor='transparent'))
    for i in range(5):
        g.add_node(pydot.Node(str(i+1)))
        g.add_edge(pydot.Edge(str(0),str(i+1)))
        for j in range(5):
            g.add_node(pydot.Node(str(j+1)+'-'+str(i+1)))
            g.add_edge(pydot.Edge(str(j+1)+'-'+str(i+1),str(j+1)))
    g.write_png('/Users/apple/Documents/graph.jpg',prog='neato')
#Let’s get back to our example with th
def plot_sift_feature(im):
    #imname = ’empire.jpg’
    #im1 = array(Image.open(imname).convert(’L’))
    tmpFile = 'tmp.sift'
    sift.process_image(im,tmpFile)
    l1,d1 = sift.read_features_from_file(tmpFile)
    figure()
    gray()
    sift.plot_features(im,l1,circle=True)
    show()

#get image from the geo location
def geoImages(longitude_min, latitude_min, longgap, latigap):
    url = 'http://www.panoramio.com/map/get_panoramas.php?order=popularity&set=public&from=0&to=20&minx=%f&miny=%f&maxx=%f&maxy=%f&size=medium' % (longitude_min, latitude_min, longgap, latigap)
    print url
    c = urllib.urlopen(url)
    # get the urls of individual images from JSON
    j = json.loads(c.read())
    imurls = []
    for im in j['photos']:
        imurls.append(im['photo_file_url'])
    return imurls

def downloadImage(urls, basePath):
    for url in urls:
        image = urllib.URLopener()
        image.retrieve(url, basePath + os.path.basename(urlparse.urlparse(url).path))
        print 'downloading:', url
    return True

def addNoise(im, noise_val = 30):
    return im + noise_val*random.standard_normal(im.shape)

def denoise(im,U_init,tolerance=0.1,tau=0.125,tv_weight=100):
    """ An implementation of the Rudin-Osher-Fatemi (ROF) denoising model
    using the numerical procedure presented in eq (11) A. Chambolle (2005).
    Input: noisy input image (grayscale), initial guess for U, weight of
    the TV-regularizing term, steplength, tolerance for stop criterion.
    Output: denoised and detextured image, texture residual. """
    m,n = im.shape #size of noisy image
    # initialize
    U = U_init
    Px = im #x-component to the dual field
    Py = im #y-component of the dual field
    error = 1
    while (error > tolerance):
        Uold = U
        # gradient of primal variable
        GradUx = roll(U,-1,axis=1)-U # x-component of U’s gradient
        GradUy = roll(U,-1,axis=0)-U # y-component of U’s gradient
        # update the dual varible
        PxNew = Px + (tau/tv_weight)*GradUx
        PyNew = Py + (tau/tv_weight)*GradUy
        NormNew = maximum(1,sqrt(PxNew**2+PyNew**2))
        Px = PxNew/NormNew # update of x-component (dual)
        Py = PyNew/NormNew # update of y-component (dual)
        # update the primal variable
        RxPx = roll(Px,1,axis=1) # right x-translation of x-component
        RyPy = roll(Py,1,axis=0) # right y-translation of y-component
        DivP = (Px-RxPx)+(Py-RyPy) # divergence of the dual field.
        U = im + tv_weight*DivP # update of the primal variable
        # update of error
        error = linalg.norm(U-Uold)/sqrt(n*m);
    return U,im-U # denoised image and texture residual

def countObject(im, binary=False):
    if binary:
        im = binaryImage(im, 128)
    labels, nbr_objects = measurements.label(im)
    print "Number of objects:", nbr_objects
    return (labels, nbr_objects)

def saveImage(im, fileName):
    return scipy.misc.imsave(fileName,im)


def addPadding(orgFile, padding):    
    postFix = orgFile.split('.')[-1]
    lastPos = orgFile.rindex(postFix) - 1
    if lastPos < 0:
        return orgFile + padding
    else:
        return '%s%s.%s' % (orgFile[:lastPos], padding, postFix)
        
def findImages(dirFile):
    return [os.path.join(dirFile, f) for f in os.listdir(dirFile) if f.lower().endswith('.jpg') or f.lower().endswith('.png')]


def cropImage(image, cropSize):
    region = image.crop(cropSize)
    return region

#Shape will reture the image size, and zeros mean create the matrix and zerorize it?
#Seems like it.
def createSameSize(image):
    #im = array(image)
    im2 = zeros(image.shape)
    return im2
    
def blurImage(im, radius_cycle):
    return filters.gaussian_filter(im, radius_cycle)


def showImageGradient(im):
    #im = array(Image.open(’empire.jpg’).convert(’L’))
    #Sobel derivative filters
    imx = zeros(im.shape)
    filters.sobel(im,1,imx)
    imy = zeros(im.shape)
    filters.sobel(im,0,imy)
    magnitude = sqrt(imx**2+imy**2)
    #Need to blur with different colors
    return (imx, imy, magnitude)
    
def blurWithColor(im, radius_cycle):
    im2 = zeros(im.shape())    
    for i in range(3):
        im2[:,:,i] = filters.gaussian_filter(im[:,:,i], i * 10)
    return im2

def binaryImage(im, threshold):
    return 1 * (im < threshold)

def pca(X):
    """ Principal Component Analysis
    input: X, matrix with training data stored as flattened arrays in rows
    return: projection matrix (with important dimensions first), variance and mean.
    """
    # get dimensions
    num_data,dim = X.shape
    # center data
    mean_X = X.mean(axis=0)
    X = X - mean_X
    if dim>num_data:
        # PCA - compact trick used
        M = dot(X,X.T) # covariance matrix
        e,EV = linalg.eigh(M) # eigenvalues and eigenvectors
        tmp = dot(X.T,EV).T # this is the compact trick
        V = tmp[::-1] # reverse since last eigenvectors are the ones we want
        S = sqrt(e)[::-1] # reverse since eigenvalues are in increasing order
        for i in range(V.shape[1]):
            V[:,i] /= S
    else:
        # PCA - SVD used
        U,S,V = linalg.svd(X)
        V = V[:num_data] # only makes sense to return the first num_data
        # return the projection matrix, the variance and the mean
        return V,S,mean_X
#This function first centers the data by subtracting the mean
def histeq(im,nbr_bins=256):
    """ Histogram equalization of a grayscale image. """
    # get image histogram
    imhist,bins = histogram(im.flatten(),nbr_bins,normed=True)
    cdf = imhist.cumsum() # cumulative distribution function
    cdf = 255 * cdf / cdf[-1] # normalize
    # use linear interpolation of cdf to find new pixel values
    im2 = interp(im.flatten(),bins[:-1],cdf)
    return im2.reshape(im.shape), cdf

def plotImageExample():
    # read image to array
    im = array(Image.open('empire.jpg'))
    # plot the image
    imshow(im)
    gray()
    # some points
    x = [100,100,400,400]
    y = [200,500,200,500]
    # plot the points with red star-markers
    plot(x,y,'r*')
    # line plot connecting the first two points
    plot(x[:2],y[:2])
    # add title and show the plot
    title('Plotting: "empire.jpg"')
    show()

try:
    print 'before open'
    grayImage = Image.open(fileName).convert('L')
    print 'opened'
    paddedFile = addPadding(fileName, '_gray')
    print 'storeFile:%s, grayImage: %r,' % (paddedFile, grayImage)
    grayImage.save(paddedFile)
    grayImage.show()
    imgFiles = findImages('/Users/apple/Documents')
    
except IOError:
    print 'error to save '
