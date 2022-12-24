function GetDevice() {
    let device = navigator.mediaDevices.getUserMedia({audio: true});
    return device;
}

function ChangeSource(value) {
    let element = document.getElementById('image')
    return element.setAttribute('src', `images/${value}.png`);
}

function BeginProcess(device) {
    device.then(
        (stream) => {
            let context = new AudioContext();
            let analyser = context.createAnalyser();
            let microphone = context.createMediaStreamSource(stream);
            let processor = context.createScriptProcessor(1024, 1, 1);

            analyser.smoothingTimeConstant = 0.8;
            analyser.fftSize = 1024;

            microphone.connect(analyser);
            analyser.connect(processor);
            processor.connect(context.destination);            

            processor.onaudioprocess = () => {
                let array = new Uint8Array(analyser.frequencyBinCount);
                analyser.getByteFrequencyData(array);
                let summary = array.reduce(
                    (previous, current) => previous + current, 0,
                );
                let average = summary / array.length;
                console.log(average);
                if (average >= 0 && average < 10) {
                    return ChangeSource('0');
                }
                else if (average >= 10 && average < 20) {
                    return ChangeSource('1');
                }
                else if (average >= 30 && average < 50) {
                    return ChangeSource('2');
                }
                else if (average >= 50 && average < 70) {
                    return ChangeSource('3');
                }  
                else if (average >= 70 && average < 100) {
                    return ChangeSource('4');
                }
                else if (average >= 100 && average < 120) {
                    return ChangeSource('5');
                }
            }
            
        }
    );
    return null;
}

let device = GetDevice();
BeginProcess(device);
