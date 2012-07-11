/**
* Hotkeys for Youtube Video
*
*
*/



HotKey = function(playerJSRef) {
    
    var player = playerJSRef;


    var legend = document.createElement('div');
    legend.setAttribute('id','floatlegend');
    legend.style.position = 'absolute';
    legend.style.width='250px';
    legend.style.padding='15px';
    legend.style.top = '20px';
    legend.style.background='white';
    legend.style.right = '20px';
    legend.style['font-size'] = '11pt'; 
    legend.style['zIndex']='100';
    legend.style.border = '2px solid';
    legend.style.display = 'none';
    legend.innerHTML = "HotKey Legend: <br /><ul>";
    legend.innerHTML += "<li>Left Arrow: Jump Back</li>";
    legend.innerHTML += "<li>Right Arrow: Jump Forward</li>";
    legend.innerHTML +=  "<li>Up/Down Arrow: Volume Control</li>"; 
    legend.innerHTML +=  "<li>p: Play/Pause</li>";
    legend.innerHTML +=  "<li>m: Mute/Unmute</li>";
    legend.innerHTML +=  "<li>c: Show/Hide Captions</li>";
    legend.innerHTML += "<li>h: Show/Hide HotKey Legend</li>";
    legend.innerHTML += "</ul>";
    document.body.insertBefore(legend,document.body.firstChild);

    

    function keyHandler(evt) {
    //console.log(evt)
    //console.log(evt.target.nodeName);
    if ((evt.target.nodeName == "BODY" ||  //only act if the hotkey was pressed on the page or player, 
         evt.target == player)) {                    //not in an actual form or textarea
        switch (evt.keyCode) {
        case 72: //h: Toggle Shortcut Key Legend
        toggleLegend();
        break;
        case 37:  //left arrow: Rewind 30 seconds
        player.seekTo(player.getCurrentTime()-30,true);
        player.playVideo()
        break;
        case 39:  //right arrow: FF 30 seconds
        player.seekTo(player.getCurrentTime()+30,true);
        player.playVideo();
        break;
        case 38:  //up arrow: Volume up 10%
        player.setVolume(Math.min(player.getVolume()+10,100));
        break;
        case 40: //down arrow: Volume down 10%
        player.setVolume(Math.max(player.getVolume()-10,0));
        break;
        case 77: //m: Toggle Mute
        if (player.isMuted()) {
            player.unMute();
        }
        else {
            player.mute();
        }
        break;
        case 80: //p: Toggle Play/Pause
        togglePlayback();
        break;
        case 67: //c: Toggle captions (may be difficult to implement)
        console.log('c');
        break;
        }
        
    };

    function togglePlayback() {
        if (player.getPlayerState() == 1 /*playing*/) {
        player.pauseVideo();
        } else {
        player.playVideo();
        }

        
    }

    function toggleLegend() {
        if (legend.style.display == "none") {
        legend.style.display = 'block';
        legend.style.top = (window.pageYOffset + 10) + 'px';
        }
        else {
        legend.style.display = 'none';
        }
    }
    };
    
    document.addEventListener('keydown',keyHandler,false);
     
    return {
    player: playerJSRef,
    };

};
