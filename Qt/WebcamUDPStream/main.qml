import QtQuick
import QtQuick.Window
import QtQuick.Particles

Window {
    width: 1024
    height: 768
    visible: true
    title: qsTr("UDP Video Stream")

    color: "#000000"

    // Imagem do vídeo UDP
    Image {
        id: videoDisplay
        anchors.fill: parent
        //fillMode: Image.PreserveAspectFit
        cache: false  // IMPORTANTE: Desativa cache para forçar reload
        //asynchronous: true  // Carregamento assíncrono para melhor performance
        source: udpClient.imageSource

    }

    // Conexão com o sinal C++
    Connections {
        target: udpClient

        function onImageSourceChanged() {
            // Força reload da imagem
            var temp = videoDisplay.source
            videoDisplay.source = ""
            videoDisplay.source = temp
        }
    }

    // Debug: Mostra quando a imagem muda de status
    Connections {
        target: videoDisplay
        function onStatusChanged() {
            //console.log("📷 Status da imagem:", videoDisplay.status)
        }
    }

    ////////////////

    // Canvas para desenhar os landmarks
    Canvas {
        id: canvas
        anchors.fill: parent

        // Conexões entre landmarks (estrutura da mão do MediaPipe)
        property var handConnections: [
            // Polegar
            [0, 1], [1, 2], [2, 3], [3, 4],
            // Indicador
            [0, 5], [5, 6], [6, 7], [7, 8],
            // Médio
            [0, 9], [9, 10], [10, 11], [11, 12],
            // Anelar
            [0, 13], [13, 14], [14, 15], [15, 16],
            // Mindinho
            [0, 17], [17, 18], [18, 19], [19, 20],
            // Palma
            [5, 9], [9, 13], [13, 17]
        ]
        /*
            onPaint: {
                var ctx = getContext("2d");
                ctx.clearRect(0, 0, width, height);

                if (!handReceiver || handReceiver.handsDetected === 0) {
                    // Mensagem quando não detecta mãos
                    ctx.fillStyle = "#666666";
                    ctx.font = "20px Arial";
                    ctx.textAlign = "center";
                    ctx.fillText("Aguardando detecção de mãos...", width/2, height/2);
                    return;
                }

                // Desenha cada mão detectada
                var hands = handReceiver.hands;

                for (var h = 0; h < hands.length; h++) {
                    var hand = hands[h];
                    var landmarks = hand.landmarks;
                    var isLeft = hand.label === "Left";

                    // Cor diferente para cada mão
                    var handColor = isLeft ? "#00FF00" : "#FF00FF"; // Verde=Esquerda, Magenta=Direita

                    // Desenha conexões
                    ctx.strokeStyle = handColor;
                    ctx.lineWidth = 2;

                    for (var i = 0; i < handConnections.length; i++) {
                        var conn = handConnections[i];
                        var start = landmarks[conn[0]];
                        var end = landmarks[conn[1]];

                        ctx.beginPath();
                        ctx.moveTo(start.x * width, start.y * height);
                        ctx.lineTo(end.x * width, end.y * height);
                        ctx.stroke();
                    }

                    // Desenha landmarks (pontos)
                    for (var j = 0; j < landmarks.length; j++) {
                        var lm = landmarks[j];
                        var x = lm.x * width;
                        var y = lm.y * height;

                        contentLoader.item.sendpatas(x, y);

                        // Círculo maior para o landmark 0 (base da mão)
                        var radius = (j === 0) ? 8 : 5;

                        ctx.beginPath();
                        ctx.arc(x, y, radius, 0, 2 * Math.PI);
                        ctx.fillStyle = handColor;
                        ctx.fill();

                        // Borda branca nos pontos
                        ctx.strokeStyle = "#FFFFFF";
                        ctx.lineWidth = 1;
                        ctx.stroke();
                    }
                }
            }

            */
    }

    // Atualiza canvas quando recebe novos dados
    Connections {
        target: handReceiver

        function onHandsDataChanged() {
            canvas.requestPaint();
        }
    }

    // Animação suave
    Timer {
        interval: 30 // ~30 FPS
        running: true
        repeat: true
        onTriggered: {
            if (handReceiver && handReceiver.handsDetected > 0) {
                canvas.requestPaint();
            }
        }
    }

    // Loader
    Loader {
        id: contentLoader
        anchors.fill: parent
        asynchronous: true
        sourceComponent: fireComp
    }

    // Componente 1
    Component {
        id: randomColorsComp

        Item {
            id: randomColorsItem

            property var handsData: handReceiver.hands
            onHandsDataChanged: {

                if(handsData, Object.keys(handsData).length === 0)
                {
                    return;
                }
                var hands = handReceiver.hands;
                if(hands.length === 2){
                    addParticle(hands[0].landmarks[8].x * width, hands[0].landmarks[8].y * height)
                    addParticle(hands[1].landmarks[8].x * width, hands[1].landmarks[8].y * height)
                }else{
                    addParticle(hands[0].landmarks[8].x * width, hands[0].landmarks[8].y * height)
                }
            }

            function sendpatas(x1,y1,x2,y2){
                console.log("###### ", x1,y1, x2,y2)
                addParticle(x1 * _stdModuleView.width, y1 * _stdModuleView.height);
                addParticle(x2 * _stdModuleView.width, y2 * _stdModuleView.height);
            }

            property bool touchReceiving: socketsTouchData.touchPoints.length > 0
            onTouchReceivingChanged: {
                console.log("->>>>>> TOUCH RECEIVING")
                if(touchReceiving){

                    if(socketsTouchData.touchPoints.length > 21){
                        addParticle(touchPointdata.touchFingerX1, touchPointdata.touchFingerY1);
                        addParticle(touchPointdata.touchFingerX2, touchPointdata.touchFingerY2);
                        console.log("-->  ADD PARTICLES  > 21", touchPointdata.touchFingerX1, touchPointdata.touchFingerY1, touchPointdata.touchFingerX2, touchPointdata.touchFingerY2)
                    }else{
                        addParticle(touchPointdata.touchFingerX1, touchPointdata.touchFingerY1);
                        console.log("-->  ADD PARTICLES  < 21")
                    }
                }
            }

            function addParticle(x, y) {
                var hue = (Date.now() % 360);
                var color = Qt.hsla(hue / 360, 0.8, 0.6, 0.8).toString();

                particles.append({
                                     x: x + rand(-20, 20),
                                     y: y + rand(-20, 20),
                                     vx: rand(-2, 2),
                                     vy: rand(-2, 2),
                                     radius: rand(2, 10),
                                     life: 1.0,
                                     decay: rand(0.01, 0.02),
                                     color: color,
                                     alpha: 1.0
                                 });

                if (particles.count > 300) {
                    particles.remove(0);
                }
            }

            function updateParticles() {
                for (var i = particles.count - 1; i >= 0; --i) {
                    var p = particles.get(i);
                    p.x += p.vx;
                    p.y += p.vy;
                    p.life -= p.decay;
                    p.alpha = p.life;

                    if (p.life <= 0) {
                        particles.remove(i);
                    } else {
                        particles.set(i, p);
                    }
                }
            }

            function rand(min, max) {
                return Math.random() * (max - min) + min;
            }

            ListModel {
                id: particles
                onCountChanged: console.log("COUNT: ", count)
            }

            Canvas {
                id: canvas
                anchors.fill: parent
                onPaint: {
                    var ctx = getContext("2d");

                    //ctx.fillStyle = "rgba(10, 10, 30, 0.01)";
                    //ctx.fillRect(0, 0, width, height);

                    for (var i = 0; i < particles.count; ++i) {
                        var p = particles.get(i);
                        var gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.radius);
                        gradient.addColorStop(0, "rgba(255, 255, 255, " + p.alpha + ")");
                        gradient.addColorStop(0.3, p.color);
                        gradient.addColorStop(1, "rgba(100, 100, 255, 0)");

                        ctx.fillStyle = gradient;
                        ctx.beginPath();
                        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                        ctx.fill();
                    }
                }
            }

            MultiPointTouchArea {
                anchors.fill: parent
                maximumTouchPoints: 2

                onPressed: (touchPoints) => {
                               for (var i = 0; i < touchPoints.length; ++i) {
                                   var tp = touchPoints[i];
                                   addParticle(tp.x, tp.y);
                               }
                           }

                onUpdated: (touchPoints) => {
                               for (var i = 0; i < touchPoints.length; ++i) {
                                   var tp = touchPoints[i];
                                   addParticle(tp.x, tp.y);
                               }
                           }
            }

            Timer {
                interval: 14  // ~60 FPS
                running: true
                repeat: true
                onTriggered: {
                    updateParticles();
                    console.log("UPDATE PARTICLES")
                    canvas.requestPaint();
                    console.log("REQUEST PAINT")
                }
            }
        }
    }

    Component {
        id: fireComp
        Item {
            id: fireItem

            property var handsData: handReceiver.hands
            property int xPos1: 0
            property int yPos1: 0
            property int xPos2: 0
            property int yPos2: 0
            property int handsCount: 0
            onHandsDataChanged: {

                if(Object.keys(handsData).length === 0)
                {
                    handsCount = 0
                    return;
                }
                var hands = handReceiver.hands;
                if(hands.length === 2){
                    handsCount = 2
                    xPos1 = hands[0].landmarks[8].x * width
                    yPos1 = hands[0].landmarks[8].y * height
                    xPos2 = hands[1].landmarks[8].x * width
                    yPos2 = hands[1].landmarks[8].y * height
                }else{
                    handsCount = 1
                    xPos1 = hands[0].landmarks[8].x * width
                    yPos1 = hands[0].landmarks[8].y * height
                }
            }

            // MouseArea para capturar a posição do mouse (precisa estar antes do ParticleSystem)
            MouseArea {
                id: mouseArea
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.CrossCursor

                property real mouseXPos: mouseX
                property real mouseYPos: mouseY
            }


            Rectangle {
                anchors.fill: parent
                color: "black"
                opacity: 0.9
            }

            // Sistema de Partículas para simular fogo
            ParticleSystem {
                id: fireSystem
                anchors.fill: parent
                running: fireItem.handsCount > 0

                // ImageParticle define a aparência das partículas
                ImageParticle {
                    system: fireSystem
                    source: "file:///C:/Users/dguimaraes/Downloads/fire.png"
                    color: "#FF6600"
                    colorVariation: 0.3
                    alpha: 0.1
                    alphaVariation: 0.1
                }

                // Emitter que segue o mouse
                Emitter {
                    id: mouseEmitter
                    system: fireSystem

                    // Posição baseada no mouse
                    x: fireItem.handsCount > 0 ? xPos1 : -100 //mouseArea.mouseXPos
                    y: fireItem.handsCount > 0 ? yPos1 : -100 //mouseArea.mouseYPos

                    width: 1
                    height: 1

                    enabled: fireItem.handsCount > 0
                    emitRate: fireItem.handsCount > 0 ? 10 : 0 //mouseArea.containsMouse ? 10 : 0

                    lifeSpan: 1500
                    lifeSpanVariation: fireItem.handsCount > 0 ? 500 : 0

                    size: 55
                    sizeVariation: 55
                    endSize: 5

                    // Velocidade para simular subida do fogo
                    velocity: AngleDirection {
                        angle: 270
                        angleVariation: 30
                        magnitude: 100
                        magnitudeVariation: 40
                    }

                    // Aceleração para simular a desaceleração do fogo ao subir
                    acceleration: AngleDirection {
                        angle: 270
                        magnitude: -30
                    }
                }
                // Emitter que segue o mouse
                Emitter {
                    id: mouseEmitter2
                    system: fireSystem

                    // Posição baseada no mouse
                    x: xPos2 //mouseArea.mouseXPos
                    y: yPos2 //mouseArea.mouseYPos

                    width: 1
                    height: 1

                    enabled: fireItem.handsCount > 0
                    emitRate: fireItem.handsCount > 0 ? 10 : 0//mouseArea.containsMouse ? 10 : 0

                    lifeSpan: 1500
                    lifeSpanVariation: fireItem.handsCount > 0 ? 500 : 0

                    size: 55
                    sizeVariation: 55
                    endSize: 5

                    // Velocidade para simular subida do fogo
                    velocity: AngleDirection {
                        angle: 270
                        angleVariation: 30
                        magnitude: 100
                        magnitudeVariation: 40
                    }

                    // Aceleração para simular a desaceleração do fogo ao subir
                    acceleration: AngleDirection {
                        angle: 270
                        magnitude: -30
                    }
                }

                // Turbulence para dar um efeito de tremulação
                Turbulence {
                    system: fireSystem
                    anchors.fill: parent
                    strength: 200
                }
            }
        }
    }
}
