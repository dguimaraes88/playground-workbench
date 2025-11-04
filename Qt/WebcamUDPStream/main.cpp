#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include "udpframeclient.h"
#include "handlandmarkreceiver.h"  // NOVO

int main(int argc, char *argv[])
{
    QGuiApplication app(argc, argv);
    QQmlApplicationEngine engine;

    // 1. Cliente UDP de vídeo
    UdpFrameClient *udpClient = new UdpFrameClient(&app);
    engine.addImageProvider("udp", new UdpFrameProvider(udpClient->receiver()));
    engine.rootContext()->setContextProperty("udpClient", udpClient);

    // 2. Receptor de Hand Landmarks (NOVO)
    HandLandmarkReceiver *handReceiver = new HandLandmarkReceiver(&app);
    engine.rootContext()->setContextProperty("handReceiver", handReceiver);

    // 3. Carrega o QML
    const QUrl url(QStringLiteral("qrc:/WebcamUDPStream/main.qml"));

    QObject::connect(
        &engine,
        &QQmlApplicationEngine::objectCreated,
        &app,
        [url](QObject *obj, const QUrl &objUrl) {
            if (!obj && url == objUrl)
                QCoreApplication::exit(-1);
        },
        Qt::QueuedConnection);

    engine.load(url);

    return app.exec();
}
