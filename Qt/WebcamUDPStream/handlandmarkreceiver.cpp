#include "handlandmarkreceiver.h"
#include <QDebug>
#include <QHostAddress>

const quint16 HAND_PORT = 8384; // Porta diferente do vídeo (8383)

HandLandmarkReceiver::HandLandmarkReceiver(QObject *parent)
    : QObject(parent)
    , m_handsDetected(0)
{
    udpSocket = new QUdpSocket(this);

    if (udpSocket->bind(QHostAddress::Any, HAND_PORT)) {
        //qDebug() << "🖐️  Hand Landmark Receiver bound to port" << HAND_PORT;
        connect(udpSocket, &QUdpSocket::readyRead,
                this, &HandLandmarkReceiver::processPendingDatagrams);
    } else {
        qCritical() << "❌ Failed to bind Hand socket:" << udpSocket->errorString();
    }
}

void HandLandmarkReceiver::processPendingDatagrams()
{
    while (udpSocket->hasPendingDatagrams()) {
        QByteArray datagram;
        datagram.resize(udpSocket->pendingDatagramSize());

        QHostAddress senderAddress;
        quint16 senderPort;
        udpSocket->readDatagram(datagram.data(), datagram.size(),
                                &senderAddress, &senderPort);

        // Debug: mostra que recebeu dados
        // qDebug() << "📦 Hand data received:" << datagram.size() << "bytes";

        // Parse JSON
        parseHandData(datagram);
    }
}

void HandLandmarkReceiver::parseHandData(const QByteArray &data)
{
    QJsonDocument doc = QJsonDocument::fromJson(data);

    if (doc.isNull() || !doc.isObject()) {
        qWarning() << "❌ Invalid JSON received";
        return;
    }

    QJsonObject root = doc.object();

    // Extrai número de mãos detectadas
    m_handsDetected = root["hands_detected"].toInt();

    // Limpa lista de mãos
    m_hands.clear();

    // Processa cada mão
    QJsonArray handsArray = root["hands"].toArray();
    for (const QJsonValue &handValue : handsArray) {
        QJsonObject handObj = handValue.toObject();

        QVariantMap hand;
        hand["hand_index"] = handObj["hand_index"].toInt();
        hand["label"] = handObj["label"].toString();
        hand["confidence"] = handObj["confidence"].toDouble();

        // Processa landmarks (21 pontos)
        QVariantList landmarks;
        QJsonArray landmarksArray = handObj["landmarks"].toArray();

        for (const QJsonValue &lmValue : landmarksArray) {
            QJsonObject lmObj = lmValue.toObject();

            QVariantMap landmark;
            landmark["x"] = lmObj["x"].toDouble();
            landmark["y"] = lmObj["y"].toDouble();
            landmark["z"] = lmObj["z"].toDouble();
            landmark["visibility"] = lmObj["visibility"].toDouble();

            landmarks.append(landmark);
        }

        hand["landmarks"] = landmarks;
        m_hands.append(hand);
    }

    // Emite sinais para atualizar QML
    emit handsDataChanged();
    emit newHandData(m_handsDetected);

    // Debug (descomente se quiser ver no console)
    // qDebug() << "📊 Hands detected:" << m_handsDetected;
}
