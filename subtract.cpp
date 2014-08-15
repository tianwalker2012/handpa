#include <opencv2/core/core.hpp>   
#include <opencv2/highgui/highgui.hpp>   
#include <opencv2/imgproc/imgproc.hpp>   
#include <iostream>   
using namespace cv;   
int main( int argc, char** argv )   
{   
    // Read image given by user   
    Mat src = imread("/Users/apple/Documents/back1.jpg", 0); // 1:color, 0:grayscale   
    Mat dst = imread("/Users/apple/Documents/add_person.jpg", 0);   
    // background subtraction   
    Mat diff;   
    absdiff(src, dst, diff);   
    threshold(diff, diff, 40, 255, CV_THRESH_BINARY); // grayscale needed      
    imshow("original", src);   
    imshow("new", dst);   
    imshow("diff", diff);   
    // Wait until user presses key   
    waitKey();   
    return 0;   
}   