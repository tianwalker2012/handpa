$(document).ready(function(){
	if(top!=self){
        top.location.replace(document.location);
    }

    function getAlwaysOneDirection()
    {
    	if ($("#oneDirection").is(":checked"))
    	{
    		return "true";
    	}
    	else
    	{
    		return "false";
    	}
    }

	$(".group1 .bw1 .button1").on("click", function(){
		$(".group1 .card-container").flip({
			direction: "lr",
			alwaysOneDirection: getAlwaysOneDirection()
		});
	})
	$(".group1 .bw1 .button2").on("click", function(){
		$(".group1 .card-container").flip({
			direction: "rl",
			alwaysOneDirection: getAlwaysOneDirection()
		});
	})
	$(".group1 .bw1 .button3").on("click", function(){
		$(".group1 .card-container").flip({
			direction: "tb",
			alwaysOneDirection: getAlwaysOneDirection()
		});
	})
	$(".group1 .bw1 .button4").on("click", function(){
		$(".group1 .card-container").flip({
			direction: "bt",
			alwaysOneDirection: getAlwaysOneDirection()
		});
	})

	$(".group1 .bw2 .button1").on("click", function(){
		$(".group1 .card-container").flip({
			speed: "1.5s",
			alwaysOneDirection: getAlwaysOneDirection()
		});
	})
	$(".group1 .bw2 .button2").on("click", function(){
		$(".group1 .card-container").flip({
			speed: "500ms",
			alwaysOneDirection: getAlwaysOneDirection()
		});
	})
	$(".group1 .bw2 .button3").on("click", function(){
		$(".group1 .card-container").flip({
			speed: "1s",
			alwaysOneDirection: getAlwaysOneDirection()
		});
	})
	$(".group1 .bw2 .button4").on("click", function(){
		$(".group1 .card-container").flip({
			speed: "2s",
			alwaysOneDirection: getAlwaysOneDirection()
		});
	})

	$(".group1 .bw3 .button1").on("click", function(){
		$(".group1 .card-container").flip({
			speed: "2s",
			timingfunction: "ease",
			alwaysOneDirection: getAlwaysOneDirection()
		});
	})
	$(".group1 .bw3 .button2").on("click", function(){
		$(".group1 .card-container").flip({
			speed: "2s",
			timingfunction: "ease-in",
			alwaysOneDirection: getAlwaysOneDirection()
		});
	})
	$(".group1 .bw3 .button3").on("click", function(){
		$(".group1 .card-container").flip({
			speed: "2s",
			timingfunction: "ease-out-cubic",
			alwaysOneDirection: getAlwaysOneDirection()
		});
	})
	$(".group1 .bw3 .button4").on("click", function(){
		$(".group1 .card-container").flip({
			speed: "2s",
			timingfunction: "ease-in-expo",
			alwaysOneDirection: getAlwaysOneDirection()
		});
	})

	$(".group1 .bw4 .button1").on("click", function(){
		$(".group1 .card-container").flip({
			alwaysOneDirection: getAlwaysOneDirection(),
			onflipping: function(currentDirection, currentTransformDirection)
			{
				if (currentTransformDirection === "fb")
				{
					alert("onflipping event: current flip direction is " + currentDirection + ", current transform direction is from front to back");
				}
				else if (currentTransformDirection === "bf")
				{
					alert("onflipping event: current flip direction is " + currentDirection + ", current transform direction is from back to front");
				}
			}
		});
	})
	$(".group1 .bw4 .button2").on("click", function(){
		$(".group1 .card-container").flip({
			direction: "tb",
			alwaysOneDirection: getAlwaysOneDirection(),
			onflipped: function(currentDirection, currentTransformDirection)
			{
				if (currentTransformDirection === "fb")
				{
					alert("onflipped event: current flip direction is " + currentDirection + ", current transform direction is from front to back");
				}
				else if (currentTransformDirection === "bf")
				{
					alert("onflipped event: current flip direction is " + currentDirection + ", current transform direction is from back to front");
				}
			}
		});
	})

	$(".group1 .bw5 .button1").on("click", function(){
		$(".group1 .card-container").flip({
			autoflip: "true",
			autoflipstart: "0",
			autoflipdelay: "1s",
			alwaysOneDirection: getAlwaysOneDirection()
		});
	})
	$(".group1 .bw5 .button2").on("click", function(){
		$(".group1 .card-container").flip({
			autoflip: "true",
			autoflipstart: "0",
			autoflipdelay: "3s",
			alwaysOneDirection: getAlwaysOneDirection()
		});
	})
	$(".group1 .bw5 .button3").on("click", function(){
		$(".group1 .card-container").flip({
			autoflip: "true",
			autoflipstart: "500ms",
			autoflipdelay: "2s",
			alwaysOneDirection: getAlwaysOneDirection()
		});
	})
	$(".group1 .bw5 .button4").on("click", function(){
		$(".group1 .card-container").flip("stopautoflip");
	})


	//group2
	$(".group2 .card-container").flip();

	$(".group2 .bw1 .button1").on("click", function(){
		$(".group2 .card-container").flip({
			autoflip: "true",
			autoflipstart: "0",
			autoflipdelay: "1s"
		});
	})
	$(".group2 .bw1 .button2").on("click", function(){
		$(".group2 .card-container").flip({
			autoflip: "true",
			autoflipstart: "0",
			autoflipdelay: "3s"
		});
	})
	$(".group2 .bw1 .button3").on("click", function(){
		$(".group2 .card-container").flip({
			autoflip: "true",
			autoflipstart: "500ms",
			autoflipdelay: "2s"
		});
	})
	$(".group2 .bw1 .button4").on("click", function(){
		$(".group2 .card-container").flip("stopautoflip");
	})

	//group3
	$(".group3 .card-container").flip();
})
