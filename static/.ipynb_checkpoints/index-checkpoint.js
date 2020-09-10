
// ############# main script ##########
// ############# initial load #########

const canvasWidth = 580;
const template = "static/data/samples/Podcast-best-movies-of-2018";

loadLabel(`${template}_${0}.wav`);
var context = new AudioContext();
var myAudio = document.getElementById("player");
var analyser = context.createAnalyser();
var src = context.createMediaElementSource(myAudio);
src.connect(analyser);
analyser.connect(context.destination);

const canvas = document.getElementById('progress').getContext('2d');

var audioChartArray;
var labelChartArray;

// ############# functions #########

function loadLabel(input) {

    var entry = {
        input: input
    }

    fetch(`${window.origin}/fetchLabels`, {

        method: 'POST',
        credentials: 'include',
        body: JSON.stringify(entry),
        cache: 'no-cache',
        headers: new Headers({
            'content-type': 'application/json'
        })

    }).then(function (response) {

        response.json().then(function(data){
            // do stuff

            document.getElementById('playerSrc').src = data['id'];
            document.getElementById('currentID').innerHTML = data['id'].split('/')[data['id'].split('/').length - 1];

            audioChartArray = data['ar'];
            labelChartArray = data['label'];

            // audio heatmap
            var trace1 = [
                {
                    z: audioChartArray,
                    type: 'heatmap',
                    colorbar: {
                        thicknessmode: 'fraction',
                        thickness: 0.01
                    }
                }
            ];

            var layout = {
                width: 640,
                height: 300,
                margin: {
                    l: 0,
                    r: 0,
                    b: 0,
                    t: 0
                }
            };
              
            Plotly.newPlot('audioChart', trace1, layout);

            // label heatmap
            var trace2 = [
                {
                    z: [labelChartArray],
                    type: 'heatmap',
                    colorbar: {
                        thicknessmode: 'fraction',
                        thickness: 0.01
                    }
                }
            ];

            var layout = {
                width: 640,
                height: 20,
                margin: {
                    l: 0,
                    r: 0,
                    b: 0,
                    t: 0
                }
            };
              
            Plotly.newPlot('labelChart', trace2, layout);

        });

    });

};

function saveLabel(input) {

    var entry = {
        input: input,
        label: labelChartArray
    };

    fetch(`${window.origin}/saveLabels`, {

        method: 'POST',
        credentials: 'include',
        body: JSON.stringify(entry),
        cache: 'no-cache',
        headers: new Headers({
            'content-type': 'application/json'
        })

    }).then(function (response) {

        response.json().then(function(data){

            // do stuff

            console.log(data['msg']);

        });

    });

};

function previewLabel(input, inputAr) {

    var entry = {
        input: input,
        label: inputAr
    };

    fetch(`${window.origin}/previewLabels`, {

        method: 'POST',
        credentials: 'include',
        body: JSON.stringify(entry),
        cache: 'no-cache',
        headers: new Headers({
            'content-type': 'application/json'
        })

    }).then(function (response) {

        response.json().then(function(data){

            // do stuff

            var fpathPreview = data['msg'].split('\\').join('/');
            document.getElementById('playerSrcPreview').src = fpathPreview;

            var contextPreview = new AudioContext();
            var myAudioPreview = document.getElementById("playerPreview");
            contextPreview.resume();
            myAudioPreview.load();
            myAudioPreview.play();

        });

    });

};

function audio_time_update() {
    var currentTime = myAudio.currentTime;
    var duration = myAudio.duration;
    var progress = canvasWidth * ( currentTime / duration );

    canvas.fillStyle = '#0f1922';
    canvas.fillRect(0,0,progress,10);
};

// ############### buttons ###########

document.getElementById('play_pause_button').addEventListener('click', () => {

    canvas.fillStyle = '#ffffff';
    canvas.fillRect(0,0,canvasWidth,100);

    context.resume();
    myAudio.load();
    myAudio.play();
   
});

document.getElementById('enter_button').addEventListener('click', () => {

    var id;

    id = document.getElementById('currentID').innerHTML.split('_')[1].split('.')[0];

    saveLabel(`${template}_${id}.wav`);

    // regex the input value, only numbers
    id = document.getElementById('mainInput').value;

    loadLabel(`${template}_${id}.wav`);

});

document.getElementById('previous_button').addEventListener('click', () => {

    var id;

    id = document.getElementById('currentID').innerHTML.split('_')[1].split('.')[0];

    saveLabel(`${template}_${id}.wav`);

    id = parseInt(id) - 1;

    loadLabel(`${template}_${id}.wav`);

});

document.getElementById('next_button').addEventListener('click', () => {

    var id;

    id = document.getElementById('currentID').innerHTML.split('_')[1].split('.')[0];

    saveLabel(`${template}_${id}.wav`);

    id = parseInt(id) + 1;

    loadLabel(`${template}_${id}.wav`);

});

document.getElementById('preview_button').addEventListener('click', () => {

    var id;

    id = document.getElementById('currentID').innerHTML.split('_')[1].split('.')[0];

    previewLabel(`${template}_${id}.wav`, labelChartArray);

});

// ############## drawing #############

var drawing = document.getElementById('drawing');
var rect = drawing.getBoundingClientRect();

const lpad = rect.left;
const rpad = rect.right;
const drawingWidth = rpad - lpad;

drawing.addEventListener('mousedown', drawingMouseDown);

function drawingMouseDown(e) {

    window.addEventListener('mousemove', drawingMouseMove);
    window.addEventListener('mouseup', drawingMouseUp);

    var prevX = e.clientX;

    const mouseLR = e.button;
    var changeVal;

    if (mouseLR == 0){
        changeVal = 0;
    } else if (mouseLR == 2){
        changeVal = 1;
    };

    function drawingMouseMove(e) {

        var newX = e.clientX;

        var p1 = (prevX - lpad) / drawingWidth;
        var p2 = (newX - lpad) / drawingWidth;

        var mx = Math.max(...[p1, p2, 0]);
        var mn = Math.min(...[p1, p2, 1]);

        var mx = Math.min(...[mx, 1]);
        var mn = Math.max(...[mn, 0]);

        mx = Math.floor( mx * labelChartArray.length );
        mn = Math.floor( mn * labelChartArray.length );

        for (var i = mn; i < mx; i++){
            labelChartArray[i] = changeVal
        };

        prevX = e.clientX;

        // update label chart
        var trace2 = [
            {
                z: [labelChartArray],
                type: 'heatmap',
                colorbar: {
                    thicknessmode: 'fraction',
                    thickness: 0.01
                }
            }
        ];

        var layout = {
            width: 640,
            height: 20,
            margin: {
                l: 0,
                r: 0,
                b: 0,
                t: 0
            }
        };
            
        Plotly.newPlot('labelChart', trace2, layout);

    };

    function drawingMouseUp(e) {

        window.removeEventListener('mousemove', drawingMouseMove);
        window.removeEventListener('mouseup', drawingMouseUp);

    };

};