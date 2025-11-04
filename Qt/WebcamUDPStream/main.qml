import QtQuick
import QtQuick.Window

Window {
    width: 640
    height: 480
    visible: true
    title: qsTr("UDP Video Stream")

    color: "#000000"

    // Imagem do vídeo UDP
    Image {
        id: videoDisplay
        anchors.fill: parent
        fillMode: Image.PreserveAspectFit
        cache: false  // IMPORTANTE: Desativa cache para forçar reload
        asynchronous: true  // Carregamento assíncrono para melhor performance
        source: udpClient.imageSource

        // Indicador de carregamento
        Text {
            anchors.centerIn: parent
            text: "Aguardando frames UDP..."
            color: "#FFFFFF"
            font.pixelSize: 20
            visible: videoDisplay.status === Image.Null || videoDisplay.status === Image.Loading
        }

        // Debug: Status da imagem
        Text {
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.margins: 10
            text: "Status: " + getStatusText()
            color: "#00FF00"
            font.pixelSize: 12

            function getStatusText() {
                switch(videoDisplay.status) {
                    case Image.Null: return "Sem imagem"
                    case Image.Ready: return "Pronto"
                    case Image.Loading: return "Carregando..."
                    case Image.Error: return "ERRO"
                    default: return "Desconhecido"
                }
            }
        }
    }

    // Conexão com o sinal C++
    Connections {
        target: udpClient

        function onImageSourceChanged() {
            console.log("🎬 Novo frame! Atualizando imagem...")
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
            console.log("📷 Status da imagem:", videoDisplay.status)
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

                    // Label da mão
                    var wristPos = landmarks[0];
                    ctx.fillStyle = handColor;
                    ctx.font = "bold 16px Arial";
                    ctx.textAlign = "center";
                    ctx.fillText(
                        hand.label + " (" + (hand.confidence * 100).toFixed(0) + "%)",
                        wristPos.x * width,
                        wristPos.y * height - 20
                    );
                }
            }
        }

        // Informações na tela
        Rectangle {
            id: infoPanel
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.margins: 10
            width: 200
            height: 80
            color: "#33000000"
            radius: 5
            border.color: "#00FF00"
            border.width: 1

            Column {
                anchors.fill: parent
                anchors.margins: 10
                spacing: 5

                Text {
                    text: "🖐️  Hand Tracking"
                    color: "#FFFFFF"
                    font.pixelSize: 14
                    font.bold: true
                }

                Text {
                    text: "Mãos detectadas: " + (handReceiver ? handReceiver.handsDetected : 0)
                    color: "#00FF00"
                    font.pixelSize: 12
                }

                Text {
                    text: handReceiver && handReceiver.handsDetected > 0 ?
                          "Verde = Esquerda\nMagenta = Direita" :
                          "Aguardando..."
                    color: "#AAAAAA"
                    font.pixelSize: 10
                }
            }
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
            interval: 33 // ~30 FPS
            running: true
            repeat: true
            onTriggered: {
                if (handReceiver && handReceiver.handsDetected > 0) {
                    canvas.requestPaint();
                }
            }
        }
}
