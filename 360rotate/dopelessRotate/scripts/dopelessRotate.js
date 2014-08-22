/*!
 * Dopeless Rotate - jQuery Plugin
 * version: 1.2.5 (24/07/2013)
 *
 * Documentation and license http://www.dopeless-design.de/dopeless-rotate-jquery-plugin-for-360-degree-product-view.html
 *
 * (c) 2013 Dopeless Design (Rostyslav Chernyakhovskyy) - mail@dopeless-design.de
 */

(function( $ ){
var is_touch_device = 'ontouchstart' in document.documentElement;

$.fn.tsRotate = function( options ) {  
    var settings = $.extend( {
        'zoom' : true,
        'reverse' : false,
        'disablelogo' : false,
        'nophp' : false,
        'nophpimglist' : '',
        'nophpzoomlist' : '',
        'startfrom' : 0,
        'zoomfolder' : 'zoomimages',
        'pathtophp' : 'dopelessRotate/scripts/',
        'hotspots' : true,
        'hotspotsTitle' : 'Specs.',
        'hotspotsFade' : true,
        'changeAxis' : false,
        'rightclass' : false,
        'leftclass' : false,
        'playstopclass' : false,
        'autorotate' : false,
        'rotateloop' : true,
        'autorotatespeed' : 100,
        'rotatehover' : false,
        'speedmultiplyer' : 1,
        'wheelRotate' : false
    }, options);
    var zoomDiv = (settings.zoom) ? '<div class="zoom"></div>' : '';
    var pointerDiv = (settings.changeAxis) ? '' : '<div class="round"><div class="pointer_object"><!--<img src="dopelessRotate/css/pointer_view.png" />--></div><div class="pointer"></div></div>';
    var hotspotsDiv = (settings.hotspots) ? '<div class="hotspots"></div>' : '';
	var direction = (settings.reverse) ? -1 : 1;
    var addLogo = (settings.disablelogo) ? '' : '<a id="dopeless_rotate_logo" title="Dopeless Rotate Plugin Home" target="_blank" href="http://www.dopeless-design.de/dopeless-rotate-jquery-plugin-360-degrees-product-viewer.html">Dopeless Rotate</a>';
    var currentFrame = settings.startfrom;
    var startFrame = settings.startfrom;
    var zoomfolder = settings.zoomfolder;
    var pathtophp = settings.pathtophp;
    var nophp = settings.nophp;
    var hotspots = settings.hotspots;
    var highlightsHidden = true;
    var changeAxis = settings.changeAxis;
    var goright = settings.rightclass;
    var goleft = settings.leftclass;
    var playstop = settings.playstopclass;
    var isautorotate = settings.autorotate;
    var isrotateloop = settings.rotateloop;
    var rotatehover = settings.rotatehover;
    if(!isrotateloop){
        var autorotateFrame = 0;
    }
    var autorotatespeed = settings.autorotatespeed;
    var speedMult = settings.speedmultiplyer;
    var wheelRotate = settings.wheelRotate;
    if(speedMult != 1){
        speedMult = speedMult/10 + 1;
    }
    var hsFade = settings.hotspotsFade;
    if(hotspots){
        var toti;     
    }
    var hotspotsTitle = settings.hotspotsTitle;
    if(nophp){
        var nophpimglist = settings.nophpimglist;
        var nophpzoomlist = settings.nophpzoomlist;
    }
    var fullpath = $(this)[0].src;
    var a = document.createElement('a');
    a.href = fullpath;
    var imgpath = a.pathname + a.search;
    var thisName = $(this).attr('id');
    if (playstop){
        if(isautorotate){
            $('.'+thisName+'.'+playstop+'').addClass('busy');
        }
    }
    var contWidth = $(this).attr('width');
    var contHeight = $(this).attr('height');
    
    var screenWidth = screen.width;
    
    if(contWidth > screenWidth){
        contHeight = Math.ceil(screenWidth*contHeight/contWidth);
        contWidth = screenWidth;
    }
    
    
    $(this).wrap('<div class="ts_holder" id="holder_'+thisName+'"/>');
    var doc = $(document);
    var holder = $('#holder_'+thisName+'');
    holder.html("<img class='ts_img_view' src='' /><img class='ts_imgzoom_view_small' src='' />"+pointerDiv+zoomDiv+"<div class='loading_bg'><div class='loading'><p>loading</p><div class='loading_bar'><div class='loading_bar_inside'></div></div></div></div><div class='zoomload_bg'><div class='zoomload_gif'></div></div></div>"+hotspotsDiv+addLogo);
    var image = $(holder).find('.ts_img_view');
    var imagezoomsmall = $(holder).find('.ts_imgzoom_view');
    var imagezoom = $(holder).find('.ts_imgzoom_view');
    var round = $(holder).find('.round');
    var contOffset = holder.offset();
    var setRoundWidth = Math.ceil(contWidth/5);
    var setPointerWidth = Math.ceil(setRoundWidth/10);
    var rotCenter = setRoundWidth/2 - setPointerWidth/2 -1;
    var rotRadius = setRoundWidth/2 - setPointerWidth;
    var setPointerObjectWidth = setRoundWidth/2-setPointerWidth*2;
    var setPointerObjectOffset = (setRoundWidth - setPointerObjectWidth)/2;
    var zoomLoadLeft = Math.round((contWidth-220)/2);
    var zoomLoadTop = Math.round((contHeight-20)/2);
    var loadingWidth = Math.round(contWidth/100*40);
    var loadingHeight = 72;
    var loadingLeft = Math.round((contWidth-loadingWidth)/2)
    var loadingTop = Math.round((contHeight-loadingHeight)/2);
    var loadingBarWidth = Math.round(loadingWidth/100*80);
    var loadingBarLeft = Math.round((loadingWidth-loadingBarWidth)/2);
    var loadingBarBottom = Math.round(loadingHeight/100*15);
    var loadingBarInsideFWidth = loadingBarWidth - 4;
    var loadingBarInsideWidth;
    var autorotate;
    var rotateright;
    var rotateleft;
    var playing = false;
    holder.bind('dragstart', function(event) { event.preventDefault() });
    holder.children().bind('dragstart', function(event) { event.preventDefault() });
    holder.css({'width':contWidth, 'height':contHeight});
    _css('.loading_bg, .zoomload_bg',{'width':contWidth, 'height':contHeight});
    _css('.zoomload_gif',{'left':zoomLoadLeft, 'top':zoomLoadTop});
    _css('.loading',{'width':loadingWidth, 'height':loadingHeight, 'left':loadingLeft, 'top':loadingTop});
    _css('.loading_bar',{'width':loadingBarWidth, 'left':loadingBarLeft, 'bottom':loadingBarBottom});
    _css('.round',{'width':setRoundWidth, 'height':setRoundWidth});
    //_css('.pointer',{'width':setPointerWidth, 'height':setPointerWidth, 'left':rotCenter, 'top':rotCenter*2});
    _css('.pointer',{'left':rotCenter, 'top':rotCenter*2});
    _css('.zoom',{'top':setRoundWidth+setRoundWidth/10+10, 'right':(setRoundWidth-30)/2-3});
    if (changeAxis){
        _css('.zoom',{'top':25, 'right':(setRoundWidth-30)/2-3});
    }
    else{
        _css('.zoom',{'top':setRoundWidth+setRoundWidth/10+10, 'right':(setRoundWidth-30)/2-3});
    }
    //_css('.pointer_object',{'width':setPointerObjectWidth, 'height':setPointerObjectWidth, 'left':setPointerObjectOffset, 'top':setPointerObjectOffset});
    holder.find('.loading_bg').fadeIn();
    function _css(elem,rules){
        holder.find(elem).css(rules);
    }
    
    var imagelist;
    var zoomlist;
    var countFrames;
    var zoomon;
    
    if(!nophp){
        /**
        $.getJSON(pathtophp+"/loadimages.php", {fname:imgpath, zoomdir:zoomfolder}, function(output) {
            imagelist = jQuery.makeArray(output.imagelist);
            zoomlist = jQuery.makeArray(output.zoomlist);
            countFrames = imagelist.length;
            preload(imagelist,countFrames);
        });
        **/
        imagelist = ImageRoot.imagelist;
        zoomlist = ImageRoot.zoomlist;
        countFrames = imagelist.length;
        preload(imagelist, countFrames); 

    }
    
    if(nophp){
        imagelist = nophpimglist.split(',');
        zoomlist = nophpzoomlist.split(',');
        countFrames = imagelist.length;
        preload(imagelist,countFrames);
    }

    function preload(arrayOfImages,countFrames) {
        
        var perc = 0;
        var thisFrame = 0;
        var cache = [];
        
        $(arrayOfImages).each(function(){
            var im = $("<img>").attr("src",this).load(function() {
                ++perc;
                //alert('current perc:'+perc);
                loadingBarInsideWidth = Math.round(loadingBarInsideFWidth/countFrames*perc);
                $(holder).find('.loading_bar_inside').css('width',loadingBarInsideWidth);
                if(perc == countFrames){
                    $(holder).find('.loading_bg').fadeOut();
                    $(holder).find('.round').fadeIn();
                    //$(holder).find('.zoom').fadeIn();
                    if(hotspots){
                       showHighlights();
                   }
                }
            });
            
            thisFrame++;
            image.attr('src', this);
            cache.push(im);
            
        });
        image.attr('src', arrayOfImages[currentFrame]);
        setPointer();
        
        if(hotspots){
            var counthotspots =  holder.parent('.dopelessrotate').find('.sethotspot').length;
            if(counthotspots < 1){
                alert('Please add at least one hotspot element (see manual)');
            }
            else{
                toti = new Array();
                holder.parent('.dopelessrotate').find('.sethotspot').each(function(index){
                    var frame = $(this).attr('href');
                    var posix = $(this).attr('posix');
                    var posiy = $(this).attr('posiy');
                    var title = $(this).attr('title');
                    var nomenu = parseInt($(this).attr('nomenu'));
                    var text = $(this).text();
                    var link = $(this).attr('link');
                    var target = $(this).attr('target');
                    if(typeof target == 'undefined'){
                        target = "_self";
                    }
                    
                    $(this).remove();
                    toti[index] = new Object();
                    toti[index]["frame"] = frame;
                    toti[index]["posix"] = posix;
                    toti[index]["posiy"] = posiy;
                    toti[index]["title"] = title;
                    toti[index]["text"] = text;
                    toti[index]["nomenu"] = nomenu;
                    toti[index]["link"] = link;
                    toti[index]["target"] = target;
                    if((index + 1) == counthotspots){
                        //holder.append('<div class="highlights"><a href="#" class="highlights_but">'+hotspotsTitle+'</a></div>');
						//for (var i = 0; i < toti.length; i++) {
                        //    if(toti[i].nomenu != 1){
                        //        holder.find('.highlights').append('<a class="highlights_item" href="'+i+'">'+toti[i].title+'</a>');
                        //        $('.highlights_item').css({'display':'none'});
                        //    }
                        //}
                        holder.append('<div class="spots blue_spots"><span class="blue_checkbox"></span><span class="blue_title">'+hotspotsTitle+'</span><span class="blue_add"></span><div class="blue_spots_items"></div></div>');
						holder.find('span.blue_checkbox, span.green_checkbox').on('click',function(){
							if ($(this).hasClass('blue_checked')){
								$(this).removeClass('blue_checked');
							} else {
								$(this).addClass('blue_checked');
							}
						});
						for (var i = 0; i < toti.length; i++) {
                            if(toti[i].nomenu != 1){
                                holder.find('.blue_spots_items').append('<a class="blue_spots_item" href="'+i+'">'+toti[i].title+'</a>');
                                $('.blue_spots_item').css({'display':'none'});
								holder.find('.hotspots').append('<div class="hotspot" id="hs'+i+'"></div>');
                            }
                        }
                    }
                });
            }
        }
        
        if(isautorotate){
            startautorotate();
        }
                
        
    }
    
    if(isautorotate){
        holder.on('mousedown',function(){
             stopautorotate();
        })
        if(is_touch_device){
            holder.on('touchstart',function(){
                stopautorotate();
            })
        }
    }
    
    if(hotspots){
        var expanded = false;
        
        $(document).on('click','.blue_title',function(e){e.preventDefault();});
    
    
        holder.find('.ts_img_view').on('click',function(){
            holder.find('.blue_spots_item').removeClass('active');
            if(expanded){
                collapseHighlight(function(){});
            }
        })
        
        holder.on('mouseenter','.blue_spots',function(){
            $(this).find('.blue_spots_item').css({'display':'block'});
            $(this).on('mouseleave',function(){
                $(this).find('.blue_spots_item').css({'display':'none'});
            })
        });
        
        holder.on('click','.blue_spots_item',function(e){
            e.stopPropagation();
            e.preventDefault(); 
        });
        
        holder.on('click','.blue_spots_item:not(.active)',function(e){
            e.stopPropagation();
            holder.find('.blue_spots_item').removeClass('active');
            $(this).addClass('active');
            var itemid = parseInt($(this).attr('href'));
            var frameno = parseInt(toti[itemid].frame);
            if (frameno != currentFrame){
                hideHighlights();   
                getFrame(frameno,itemid);
            }
            else{
                if(expanded){   
                    collapseHighlight(function(){
                        expandHighlight(itemid); 
                    });
                }
                else{
                    expandHighlight(itemid); 
                }
            }
        });
        
        holder.on( 'click', '.hotspot:not(.expanded)', function(e){
            e.stopPropagation();
            var itemid = parseInt($(this).attr('id').replace('hs',''));
            if(expanded){
                collapseHighlight(function(){
                    expandHighlight(itemid); 
                });
            }
            else{
                expandHighlight(itemid); 
            }
            
        });
        
        
        if(!is_touch_device){
            holder.on( 'click', '.expanded', function(e){
                e.stopPropagation();
                holder.find('.blue_spots_item').removeClass('active');
                if(expanded){
					collapseHighlight(function(){});
				}
            })
        }
        
        if(is_touch_device){
			//展开spots列表
            holder.on('touchstart','span.blue_title',function(e){
                e.stopPropagation();	//阻止冒泡
				e.preventDefault();		//阻止后面将要执行的事件
				holder.find('.blue_spots_item').css({'display':'block'});
            });
			
			//CheckBox勾选状态变更
			holder.on('touchstart','span.blue_checkbox, span.green_checkbox',function(e){
                e.stopPropagation();
                e.preventDefault(); 
                if ($(this).hasClass('blue_checked')){
					$(this).removeClass('blue_checked');
				} else {
					$(this).addClass('blue_checked');
				}
            });
            
			//展示spot的文字信息
            holder.on('touchstart','.hotspot',function(e){
                e.stopPropagation();
                e.preventDefault();
				var itemid = parseInt($(this).attr('id').replace('hs',''));
				var frameno = parseInt(toti[itemid].frame);
				getFrame(frameno,itemid);
				if (expanded){
					collapseHighlight(function(){
						expandHighlight(itemid); 
					});
				} else {
					expandHighlight(itemid); 
				}
            });
			
			holder.on('touchstart','.blue_spots_item',function(e){
                e.stopPropagation();
				e.preventDefault();
				var itemid = parseInt($(this).attr('href'));
				var frameno = parseInt(toti[itemid].frame);
				getFrame(frameno,itemid);
				holder.find('.blue_spots_item').css({'display':'none'});
				if (expanded){   
					collapseHighlight(function(){
						expandHighlight(itemid); 
					});
				} else{
					expandHighlight(itemid); 
				}
            });
			
			/*
			holder.on('touchend','.blue_spots_item:not(.active)',function(e){
                e.stopPropagation();
				alert(444);
                holder.find('.blue_spots_item').removeClass('active');
                $(this).addClass('active');
                var itemid = parseInt($(this).attr('href'));
                var frameno = parseInt(toti[itemid].frame);
                if (frameno != currentFrame){
                    hideHighlights();   
                    getFrame(frameno,itemid);
                }
                else{
                    if(expanded){
                        collapseHighlight(function(){
                            expandHighlight(itemid); 
                        });
                    }
                    else{
                        expandHighlight(itemid); 
                    }
                }
            });
			
			holder.on( 'touchend', '.hotspot:not(.expanded)', function(e){
                e.stopPropagation();
				alert(555);
                var itemid = parseInt($(this).attr('id').replace('hs',''));
                if(expanded){
                    collapseHighlight(function(){
                        expandHighlight(itemid); 
                    });
                }
                else{
                    expandHighlight(itemid); 
                }
            });
			
			holder.on( 'touchend', '.expanded', function(e){
                e.stopPropagation();
				alert(666);
                holder.find('.blue_spots_item').removeClass('active');
                collapseHighlight();
            })
			
			/*
            holder.on('touchend','.blue_spots_item',function(e){
                e.stopPropagation();
                e.preventDefault(); 
            });
			*/
			
        }
    
        function getFrame(frameno,itemid){
            (function step() {
                    if(currentFrame > frameno){
                        currentFrame--;  
                        image.attr('src', imagelist[currentFrame]);
                        if(currentFrame == frameno){
                            startFrame = currentFrame;
                            //showHighlights(itemid);
                            alphaHighlights(itemid);
                            setPointer();
                        }
                        else{
                            setTimeout(step, 30);
                        }
                    }
                    if(currentFrame < frameno){
                        currentFrame++;  
                        image.attr('src', imagelist[currentFrame]);
                        if(currentFrame == frameno){
                            startFrame = currentFrame;
                            //showHighlights(itemid);
                            alphaHighlights(itemid);
                            setPointer();
                        }
                        else{
                            setTimeout(step, 30);
                        }
                    }
            })();
        }  
        
        function alphaHighlights(itemid){
            //holder.find('.expanded').removeClass('expanded').find('.hltitle,.hltext').remove();
            holder.find('.hltitle,.hltext').remove();
            holder.find('.blue_spots_item').removeClass('active');
			var rspeed = 5;
            for (var i = 0; i < toti.length; i++) {
                //if(toti[i].frame == currentFrame){
                    var distance = currentFrame - toti[i].frame;
					//holder.append('<div class="hotspot" id="hs'+i+'"></div>');
                    holder.find('#hs'+i+'').css({
                        'top':toti[i].posiy + '%',
                        'left':(toti[i].posix - distance*rspeed) + '%',
                        'display':'block',
						'opacity':(1 - Math.abs(distance/countFrames)*rspeed*0.8)
                    });
					//$(this).find("span").css('opacity','0.5');
					//holder.find('#hs'+i+'').css('opacity', String(1 - distance/currentFrame));
                    //}).fadeIn(5);
				
				if(toti[i].posix > 60){
					holder.find('#hs'+i+'').addClass('posr');
				}
				if(toti[i].posiy > 75){
					holder.find('#hs'+i+'').addClass('posb');
				}
                
            }
            
            //if(itemid !== undefined){
            //    expandHighlight(itemid);
            //}
            highlightsHidden = false;
        }
        
        function showHighlights(itemid){
            //holder.find('.expanded').removeClass('expanded').find('.hltitle,.hltext').remove();
            holder.find('.hltitle,.hltext').remove();
            holder.find('.blue_spots_item').removeClass('active');
            for (var i = 0; i < toti.length; i++) {    
                if(toti[i].frame == currentFrame){
                    
                    holder.append('<div class="hotspot" id="hs'+i+'"></div>');
                    holder.find('#hs'+i+'').css({
                        'top':toti[i].posiy+'%',
                        'left':toti[i].posix+'%'
                    }).fadeIn(50);
                    if(toti[i].posix > 60){
                        holder.find('#hs'+i+'').addClass('posr');
                    }
                    if(toti[i].posiy > 75){
                        holder.find('#hs'+i+'').addClass('posb');
                    }
                    
                }
            }
            
            if(itemid !== undefined){
                expandHighlight(itemid);
            }
            highlightsHidden = false;
        }
		
        function hideHighlights(){
            if(expanded){
                collapseHighlight(function(){
                    holder.find('.blue_spots_item').removeClass('active');
                    //if(hsFade){
                    if(false){
                        holder.find('.hotspot').fadeOut(150, function(){
                            $(this).remove();
                        });
                    }
                    else{
                        holder.find('.hotspot').css({'display':'none'});
                        $(this).remove();
                    }
                    highlightsHidden = true;
                })
            }
            else{
                holder.find('.blue_spots_item').removeClass('active');
                //if(hsFade){
                if(false){
                    holder.find('.hotspot').fadeOut(150, function(){
                        $(this).remove();
                    });
                }
                else{
                    holder.find('.hotspot').css({'display':'none'});
                    $(this).remove();
                }
                highlightsHidden = true;
            }
        }
        
		//展开信息点
        function expandHighlight(itemid){
			if(itemid !== undefined){
                holder.find('.blue_spots_item').removeClass('active');
                holder.find('.blue_spots_item[href="'+itemid+'"]').addClass('active');
				$('.text_box').css({'display':'block'});
                //holder.find('#hs'+itemid+'').addClass('expanded').append('<span class="hltitle">'+toti[itemid].title+'</span>');
				holder.find('#hs'+itemid+'').addClass('expanded');
				if(toti[itemid].text){
                    if(toti[itemid].link){
						$('.text_info p').prepend('<a class="hltext link" href="'+toti[itemid].link+'" target="'+toti[itemid].target+'">'+toti[itemid].text+'</a>');
					}
					else{
						$('.text_info p').prepend('<span class="hltext">'+toti[itemid].text+'</span>');
					}
                }
				
				/*
                if(toti[itemid].text){
                    if (holder.find('#hs'+itemid+'').is('.posb')) {
                        if(toti[itemid].link){
                            holder.find('#hs'+itemid+'').prepend('<a class="hltext link" href="'+toti[itemid].link+'" target="'+toti[itemid].target+'">'+toti[itemid].text+'</a>');
                        }
                        else{
                            holder.find('#hs'+itemid+'').prepend('<span class="hltext">'+toti[itemid].text+'</span>');
                        }
                    }
                    else{
                        if(toti[itemid].link){
                            holder.find('#hs'+itemid+'').append('<a class="hltext link" href="'+toti[itemid].link+'" target="'+toti[itemid].target+'">'+toti[itemid].text+'</a>');
                        }
                        else{
                            holder.find('#hs'+itemid+'').append('<span class="hltext">'+toti[itemid].text+'</span>');
                        }
                    }
                }
                if (holder.find('#hs'+itemid+'').is('.posr')) {
                    var hsposition = holder.find('#hs'+itemid+'').position();
                    holder.find('#hs'+itemid+'').css({'left':'0px'});
                    var hswidth = holder.find('#hs'+itemid+'').outerWidth();
                    var newhsposition = hsposition.left - hswidth + 20;
                    holder.find('#hs'+itemid+'').css({'left':newhsposition+'px'});
                } 
                if (holder.find('#hs'+itemid+'').is('.posb')) {
                    var hsposition = holder.find('#hs'+itemid+'').position();
                    holder.find('#hs'+itemid+'').css({'top':'0px'});
                    var hsheight = holder.find('#hs'+itemid+'').outerHeight();
                    var newhsposition = hsposition.top - hsheight + 20;
                    holder.find('#hs'+itemid+'').css({'top':newhsposition+'px'});
                }
				*/
                expanded = true;
            }
        }
        
		//收起信息点
        function collapseHighlight(callback){
            var itemid = parseInt(holder.find('.expanded').attr('id').replace('hs',''));
            //holder.find('.expanded').css({'top':toti[itemid].posiy+'%','left':toti[itemid].posix+'%'}).removeClass('expanded').find('.hltitle,.hltext').remove();
            holder.find('.expanded').removeClass('expanded');
            expanded = false;
            $('.text_box').css({'display':'none'});
			if(callback){
                callback();
            }
        }
    
    }
    
    function startautorotate(rtl){
        playing = true;
        if(!rtl){
            autorotate = setInterval(nextFrame, autorotatespeed);
        }
        if(rtl){
            autorotate = setInterval(prevFrame, autorotatespeed);
        }
        
        if(playstop){
            $('.'+thisName+'.'+playstop+'').addClass('busy');
        }
    }
    
    function stopautorotate(){
        clearInterval(autorotate);
        playing = false;
        isrotateloop = true;
        if(playstop){
            $('.'+thisName+'.'+playstop+'').removeClass('busy');
        }
    }
    
    
    function setPointer(){
        var corner = Math.floor(360/countFrames)*direction;                     
        var degrees = corner*currentFrame;                              
        var radians=degrees*Math.PI/180;
        var sine=Math.sin(radians);
        var cose=Math.cos(radians);
        var poinx = rotCenter+rotRadius*sine*-1;
        var poiny = rotCenter+rotRadius*cose;
        _css('.pointer',{'left':poinx, 'top':poiny});
    }
    
    function rotateImg(enterPosition){  
        doc.on('mousemove.dragrotate', function(e){
            
            
            if(changeAxis){
                var cursorPosition = e.pageY - contOffset.top;
            }
            else{
                var cursorPosition = e.pageX - contOffset.left;
            }
            var xOffset = cursorPosition - enterPosition;
            
            
            
            var step = Math.round(contWidth/countFrames)*direction;
            var frameOffset = Math.round(xOffset/step);
            var cycles = Math.abs(Math.floor((frameOffset+startFrame)/countFrames));
            currentFrame = startFrame + frameOffset;
            
            if(hotspots){
                if(currentFrame != startFrame){
                    hideHighlights();
                }
            }
            alphaHighlights();
			
            if(currentFrame >= countFrames){
                currentFrame = currentFrame - countFrames*cycles;
            }       
            if(currentFrame < 0){
                currentFrame = countFrames*cycles + currentFrame;
            }
            image.attr('src', imagelist[currentFrame]);
            if(!changeAxis){
                setPointer();
            }
        });
        doc.on('mouseup.dragrotate', function(){
            if(hotspots && highlightsHidden){
                //showHighlights();
                alphaHighlights();
            }
            startFrame = currentFrame;
            doc.off('.dragrotate');
        });
        if(rotatehover){
            holder.on('mouseleave.dragrotate', function(){
                if(hotspots && highlightsHidden){
                    showHighlights();
                }
                startFrame = currentFrame;
                doc.off('.dragrotate');
            });
        }
    }
    
    function rotateImgMobile(enterPosition){    
        holder.on('touchmove.dragrotatemob', function(mobileEvent) {
           
            var event = window.event;
            if(changeAxis){
                var cursorPosition = event.touches[0].pageY - contOffset.top;
            }
            else{
                var cursorPosition = event.touches[0].pageX - contOffset.left;
            }
            var xOffset = cursorPosition - enterPosition;
            var step = Math.round(contWidth/countFrames)*direction;
            var frameOffset = Math.round(xOffset/step);
            var cycles = Math.abs(Math.floor((frameOffset+startFrame)/countFrames));
            currentFrame = startFrame + frameOffset;
            
            if(hotspots){
                if(currentFrame != startFrame){
                    hideHighlights();
                }
            }
            alphaHighlights();
            if(currentFrame >= countFrames){
                currentFrame = currentFrame - countFrames*cycles;
            }       
            if(currentFrame < 0){
                currentFrame = countFrames*cycles + currentFrame;
            }
            image.attr('src', imagelist[currentFrame]);
            if(!changeAxis){
                setPointer();
            }
        });
        holder.on('touchend.dragrotatemob', function(mobileEvent) {
            if(hotspots && highlightsHidden){
                //showHighlights();
                alphaHighlights();
            }
            startFrame = currentFrame;
            holder.off('.dragrotatemob');
        });
        
    }
    
    function zoomImg(startXpos,startYpos,offset){
        alert("zoomImg");
		zoomon = true;
        if(hotspots){
            hideHighlights();
        }
        holder.find('.blue_spots').fadeOut();
        var zoomloading = true;
        holder.find('.round').fadeOut();
        //holder.find('.zoom').fadeOut();  
        var zoomImg = new Image();
        zoomImg.src = zoomlist[currentFrame];
        if (zoomImg.complete || zoomImg.readystate === 4) {
        }
        else {
            //holder.find('.zoomload_bg').fadeIn();
        }
        zoomImg.onload = function() {
            zoomHeight = zoomImg.height;
            zoomWidth = zoomImg.width;
            var leftOverflow = (zoomWidth - contWidth)/-2;
            var topOverflow = (zoomHeight - contHeight)/-2;
            imagezoomsmall.attr('src', imagelist[currentFrame]);
			imagezoomsmall.css({'left':leftOverflow, 'top':topOverflow});
            imagezoom.attr('src', zoomlist[currentFrame]);
            imagezoom.css({'left':leftOverflow, 'top':topOverflow});
    
            image.animate({
                width: zoomWidth,
                height: zoomHeight,
                left:leftOverflow,
                top:topOverflow
                }, 100, 'linear', function() {
                    imagezoomsmall.animate({
                    width: zoomWidth,
                    height: zoomHeight,
                        left:leftOverflow,
                        top:topOverflow
                        }, 100, 'linear', function() {
                            imagezoomsmall.fadeIn(100);
                        });
					imagezoom.animate({
                    width: zoomWidth,
                    height: zoomHeight,
                        left:leftOverflow,
                        top:topOverflow
                        }, 100, 'linear', function() {
                            imagezoom.fadeIn(100);
                        });
                    });

            //holder.find('.zoomload_bg').fadeOut();
            holder.addClass('zoomout');
            var zoomloading = false;

            holder.on('mousemove.dragpan', (function(e){
                var hMoveLock = false;
                var vMoveLock = false;
                var currentXpos = e.pageX - offset.left;
                var currentYpos = e.pageY - offset.top;
                var xlimit = (zoomWidth-contWidth)*-1;
                var ylimit = (zoomHeight-contHeight)*-1;

                var xSpeedCoeff = Math.floor(zoomWidth/contWidth)*speedMult;
                var ySpeedCoeff = Math.floor(zoomHeight/contHeight)*speedMult;
                var moveLeft = startXpos - currentXpos;
                var moveTop = startYpos - currentYpos;
                var leftOffset = leftOverflow + moveLeft*xSpeedCoeff;
                var topOffset = topOverflow + moveTop*ySpeedCoeff;
                    
                if(leftOffset >= 0){
                    hMoveLock = true;
                    startXpos = startXpos - leftOffset;
                } 
                if(leftOffset <= xlimit){
                    hMoveLock = true;
                    startXpos = startXpos - leftOffset + xlimit;    
                }
                if(topOffset >= 0){
                    vMoveLock = true;
                    startYpos = startYpos - topOffset;
                } 
                if(topOffset <= ylimit){
                    vMoveLock = true;
                    startYpos = startYpos - topOffset + ylimit; 
                }
                if(!hMoveLock) {
                    imagezoom.css('left', leftOffset);
                    imagezoomsmall.css('left', leftOffset);
                }
                if(!vMoveLock) {
                    imagezoom.css('top', topOffset);
                    imagezoomsmall.css('top', topOffset);
                }
            }));
            doc.on('mousedown.zoomof', (function(){
                if(!zoomloading){
                   zoomOut();
                }
            }));
        };  
    }
    
    function zoomMoveMobile(startXpos,startYpos,offset,leftOverflow,topOverflow){
        var sieventm = window.event;
        var currentXpos = sieventm.touches[0].pageX - offset.left;
        var currentYpos = sieventm.touches[0].pageY - offset.top;   
        var xlimit = (zoomWidth-contWidth)*-1;
        var ylimit = (zoomHeight-contHeight)*-1;
        var xSpeedCoeff = Math.floor(zoomWidth/contWidth)*speedMult;
        var ySpeedCoeff = Math.floor(zoomHeight/contHeight)*speedMult;
        var moveLeft = startXpos - currentXpos;
        var moveTop = startYpos - currentYpos;
        var leftOffset = leftOverflow + moveLeft*xSpeedCoeff*-1;
        var topOffset = topOverflow + moveTop*ySpeedCoeff*-1;
            if(leftOffset >= 0){
                leftOffset = 0;
            }
            if(leftOffset <= xlimit){
                leftOffset = xlimit;
            }
            if(topOffset >= 0){
                topOffset = 0;
            }
            if(topOffset <= ylimit){
                topOffset = ylimit;
            }
			imagezoomsmall.css('left', leftOffset);
            imagezoomsmall.css('top', topOffset);
            //imagezoom.css('left', leftOffset);
            //imagezoom.css('top', topOffset);
            
        holder.on('touchend.zoomendmob',(function(){
                    holder.off('.mobdragpan');
                    newleftOverflow = leftOffset;
                    newtopOverflow = topOffset;
                }));
    }
    
    var newleftOverflow;
    var newtopOverflow;
    
    function zoomImgMobile(offset){
		zoomon = true;
        if(hotspots){
            hideHighlights();
        }
        holder.find('.blue_spots').fadeOut();
        $(document).find('.blue_spots_item').css({'display':'none'});
        var zoomloading = true;
        holder.find('.round').fadeOut();
        //holder.find('.zoom').fadeOut();  
        
		zoomloading = false;
		//image.attr('src', imagelist[currentFrame]);
		
		holder.on('gesturechange.scaleimage', function(mobileEvent) {
			mobileEvent.preventDefault()
			var event = window.event;
			var curscale = event.scale;
			//$('.onionbox').html(curscale);
			image.css('width', contWidth * curscale);
			image.css('height', contHeight * curscale);
			//image.css({'width':contWidth * curscale,'height':contHeight * curscal});
			
			holder.on('touchmove.dragstartmob', (function(e){
				var event = window.event;
				var leftOffset;
				var topOffset;
				
				if (event.touches.length > 1) {
					leftOffset = (event.touches[0].pageX + event.touches[1].pageX - image.width())/2;
					topOffset = (event.touches[0].pageY + event.touches[1].pageY - image.height())/2;
					image.css('left', leftOffset);
					image.css('top', topOffset);
				}
				
			}));
		});
		
		holder.on('gestureend.scaleimage', function(mobileEvent) {
			holder.off('.scaleimage');
			if(!zoomloading){
				zoomOut();
			}
		});
		
		
		
		holder.on('touchend.dragstartmob', function() {
			//holder.off('.dragstartmob');
		});
    }
    
    
    function zoomOut(){
        if(hotspots && highlightsHidden){
            showHighlights();
            holder.find('.blue_spots').fadeIn();
        }
        holder.off('.dragpan');
        holder.off('mousedown.zoomof');
        holder.off('.zoomendmob');
        holder.off('.dragstartmob');
        image.attr('src', imagelist[currentFrame]);
        image.css({'left':0,'top':0,'width':contWidth,'height':contHeight});
		image.animate({
            width: contWidth,
            height: contHeight,
            left:0,
            top:0
            }, 100, 'linear', function() {
                image.fadeIn(100);
                });
        imagezoom.animate({
            width: contWidth,
            height: contHeight,
            left:0,
            top:0
            }, 100, 'linear', function() {
                imagezoom.fadeOut(100);
                });
        holder.find('.round').fadeIn();
        //holder.find('.zoom').fadeIn();          
        holder.removeClass('zoomout');
        zoomon = false;
    }
    
    
    
    holder.on('mousedown.initrotate', function(e){
        
        if(!zoomon){
            if(changeAxis){
                var enterPosition = e.pageY - contOffset.top;
            }
            else{
                var enterPosition = e.pageX - contOffset.left;
            }
            rotateImg(enterPosition);
        }
    });
    
    if(wheelRotate){
        holder.on('mousewheel',function(e){
            if(!zoomon){
                e.preventDefault();
                if(playing){
                    stopautorotate();
                }
                if(e.originalEvent.wheelDelta /120 > 0) {
                    nextFrame();
                }
                else{
                    prevFrame();
                }
            }
        })
    }
    
    if(rotatehover){
        holder.on('mouseenter.initrotate', function(e){
        
        if(!zoomon){
            if(changeAxis){
                var enterPosition = e.pageY - contOffset.top;
            }
            else{
                var enterPosition = e.pageX - contOffset.left;
            }
            rotateImg(enterPosition);
        }
        });
    }
    
    holder.find('.zoom').on('click.initzoom', function(e){
        var offset = holder.offset();
        var startXpos = e.pageX - offset.left;
        var startYpos = e.pageY - offset.top;
        zoomImg(startXpos,startYpos,offset);
    });
    
    
    
   
    if(is_touch_device){
    
        holder.find(image).on('touchstart.initrotatemob', function(mobileEvent){
			if(hotspots){
                //清屏（收起spots列表，清除文字信息）
				holder.find('.blue_spots_item').css({'display':'none'});
				if(expanded){
					collapseHighlight(function(){});
				}
            }
            if(!zoomon){
                mobileEvent.preventDefault();
                var sevent = window.event;
                if(changeAxis){
                    var enterPosition = sevent.touches[0].pageY - contOffset.top;
                }
                else{
                    var enterPosition = sevent.touches[0].pageX - contOffset.left;
                }
                rotateImgMobile(enterPosition);
            }
        });
		
		holder.on('gesturestart.gestureimage', function(mobileEvent){
			holder.off('.dragrotatemob');
			mobileEvent.preventDefault();
			//scaleImgMobile();
			//zoomImg(startXpos,startYpos,offset);
			var offset = holder.offset();
			zoomImgMobile(offset);
        });
		
        holder.find('.zoom').on('touchstart.initzoommob', function(mobileEvent){
            mobileEvent.preventDefault();
            var offset = holder.offset();
            zoomImgMobile(offset);  
        }); 
    }
    
    function scaleImgMobile(){
		holder.on('gesturechange.scaleimage', function(mobileEvent) {
			mobileEvent.preventDefault()
			var event = window.event;
			var curscale = event.scale;
			$('.onionbox').html(curscale);
			//contWidth *= curscale;
			//contHeight *= curscale;
			holder.find('.ts_img_view').css({'width':contWidth * curscale, 'height':contHeight * curscale});
			holder.css({'width':contWidth * curscale, 'height':contHeight * curscale});
		});
		holder.on('gestureend.scaleimage', function(mobileEvent) {
            var event = window.event;
			var curscale = event.scale;
			contWidth *= curscale
            contHeight *= curscale
			holder.off('.scaleimage');
        });
	}
	
    function nextFrame(){
        //if(hotspots){
            hideHighlights();
        //}
        
        currentFrame++;
        
        if(currentFrame >= countFrames){
            currentFrame = 0;
        }
        image.attr('src', imagelist[currentFrame]);
        if(!changeAxis){
            setPointer();
        }
        
        startFrame = currentFrame;
        if(hotspots){
            //showHighlights();
            alphaHighlights();
        }
        if(!isrotateloop){
            autorotateFrame = autorotateFrame + 1;
            if(autorotateFrame == countFrames){
                stopautorotate();
            }
        }
    }
    
    function prevFrame(){
        if(hotspots){
                hideHighlights();
            }
            
            currentFrame--;
            
            if(currentFrame < 0){
                currentFrame = countFrames;
            }
            image.attr('src', imagelist[currentFrame]);
            if(!changeAxis){
                setPointer();
            }
            
            startFrame = currentFrame;
            if(hotspots){
                //showHighlights();
                alphaHighlights();
            }
    }
    
    
 
    if(goright){
        $('.'+thisName+'.'+goright+'').on('click',function(){
            stopautorotate();
            nextFrame();
        })
        
        $('.'+thisName+'.'+goright+'').on('mousedown touchstart',function(){
            stopautorotate();
            if(!playing){
                startautorotate();
                $(this).on('mouseleave mouseup touchend touchmove',function(){
                    stopautorotate();
                })
            }
        })
    }
    
    
    
    if(goleft){
        $('.'+thisName+'.'+goleft+'').on('click',function(){
            stopautorotate();
            prevFrame();
        })
        $('.'+thisName+'.'+goleft+'').on('mousedown touchstart',function(){
            stopautorotate();
            if(!playing){
                startautorotate(true);
                $(this).on('mouseleave mouseup touchend touchmove',function(){
                    stopautorotate();
                })
            }
        })
    }
    
    if(playstop){
        $('.'+thisName+'.'+playstop+'').on('click',function(){
            if(playing){
                stopautorotate();
            }
            else{
                startautorotate();
            }
            
        })
    }
};
})( jQuery );