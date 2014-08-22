(function(window, $) {
    var Rotate = {
        initialize: function() {
			
			/* Browser Check */
			var isTablet;
			isTablet = browserCheck();
			
			/* Window Resize */
			var imgWidth, imgHeight, imgScole;
			imgWidth = $('#rotateimage').attr('width');
			imgHeight = $('#rotateimage').attr('height');
			imgScole = imgHeight/imgWidth;
			
			$(window).resize(function() {
				if (!isTablet) {
					//resizeImgOnPC();
				}
			});
			
			/* Full Screen Change */
			if (isTablet) {
				resizeTablet(imgScole);
			}
			
			/* Change Orientation */
			if (isTablet) {
				changeOrientation(imgScole);
			}

        }
    };

    $(document).ready(function() {
        Rotate.initialize();
    });

    window.Rotate = window.Rotate || {};
    window.Rotate = Rotate;
})(window, window.jQuery);

/* Browser Check */
function browserCheck() {
	var sUserAgent = navigator.userAgent.toLowerCase();
	var bIsIpad = sUserAgent.match(/ipad/i) == "ipad";
	var bIsIphoneOs = sUserAgent.match(/iphone os/i) == "iphone os";
	var bIsMidp = sUserAgent.match(/midp/i) == "midp";
	var bIsUc7 = sUserAgent.match(/rv:1.2.3.4/i) == "rv:1.2.3.4";
	var bIsUc = sUserAgent.match(/ucweb/i) == "ucweb";
	var bIsAndroid = sUserAgent.match(/android/i) == "android";
	var bIsCE = sUserAgent.match(/windows ce/i) == "windows ce";
	var bIsWM = sUserAgent.match(/windows mobile/i) == "windows mobile";
	
	if (bIsIpad || bIsIphoneOs || bIsMidp || bIsUc7 || bIsUc || bIsAndroid || bIsCE || bIsWM) {
		//alert("Your useragent is phone.");
		return true;
	} else {
		//alert("Your useragent is pc.");
		return false;
	}
}

/* Change Orientation */
function changeOrientation(scole) {
	$(window).bind( 'orientationchange', function(e){
		if (window.orientation == 0 || window.orientation == 180) {
			//alert("portrait ShuPing");
			resizeTablet(scole);
		} else if (window.orientation == 90 || window.orientation == -90) {
			//alert("landscape HengPing");
			resizeTablet(scole);
		}
	});
}

/* Resize Rotate Image */
function resizeTablet(scole) {
	var winWidth = $(window).innerWidth();
	var winHeight = $(window).innerHeight();
	$('.rotatebox').css({'width' : winWidth, 'height' : $(window).innerWidth() * scole, 'border' : 'none'});
	$('.text_box').css({'height' : 100});
	$('.text_box .text_info').css({'margin-top' : 10, 'height' : 70});
	//change '#rotateimage' css
	$('img#rotateimage').attr('width', $(window).innerWidth());
	$('img#rotateimage').attr('height', $(window).innerWidth() * scole);
}

function resizeTablet2(scole) {
	alert("resizeTablet2");
	var winWidth = $(window).innerHeight();
	var winHeight = $(window).innerWidth();
	$('.rotatebox').css({'width' : winWidth, 'height' : winHeight, 'border' : 'none'});
	//change '#rotateimage' css
	$('img#rotateimage').attr('width', $(window).innerWidth());
	$('img#rotateimage').attr('height', $(window).innerWidth() * scole);
}

/* Resize Image On OC */
function resizeImgOnPC() {
	if ($(window).width()>=500) {
		//alert(">900");
		$('.rotatebox').css('width' , '800px');
		$('.rotatebox').css('height' , '640px');
		$("#rotateimage").attr("width", "800");
		$("#rotateimage").attr("height", "640");
	} else if ($(window).width()<=500) {
		//alert("<900");
		$('.rotatebox').css('width' , '320px');
		$('.rotatebox').css('height' , '252px');
		$("#rotateimage").attr("width", "320");
		$("#rotateimage").attr("height", "252");
	}
}





