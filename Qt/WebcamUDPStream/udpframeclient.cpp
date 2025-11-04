#include "udpframeclient.h"
#include <QDebug>
#include <QHostAddress>
#include <QMutexLocker>
#include <vector>

const quint16 SERVER_PORT = 8383;

// ==================== UdpFrameReceiver ====================
UdpFrameReceiver::UdpFrameReceiver(QObject *parent)
    : QObject(parent)
{
    udpSocket = new QUdpSocket(this);

    if (udpSocket->bind(QHostAddress::Any, SERVER_PORT)) {
        qDebug() << "UDP Server bound to port" << SERVER_PORT;
        connect(udpSocket, &QUdpSocket::readyRead,
                this, &UdpFrameReceiver::processPendingDatagrams);
    } else {
        qCritical() << "Failed to bind UDP socket:" << udpSocket->errorString();
    }
}

void UdpFrameReceiver::processPendingDatagrams()
{
    while (udpSocket->hasPendingDatagrams()) {
        QByteArray datagram;
        datagram.resize(udpSocket->pendingDatagramSize());

        QHostAddress senderAddress;
        quint16 senderPort;
        udpSocket->readDatagram(datagram.data(), datagram.size(),
                                &senderAddress, &senderPort);

        // Debug: Mostra que recebeu dados
        qDebug() << "📦 Recebido:" << datagram.size() << "bytes de" << senderAddress.toString();

        try {
            std::vector<uchar> buf(datagram.begin(), datagram.end());
            // OpenCV 2.4.13: Use CV_LOAD_IMAGE_COLOR em vez de cv::IMREAD_COLOR
            cv::Mat frame_mat = cv::imdecode(cv::Mat(buf), CV_LOAD_IMAGE_COLOR);

            if (!frame_mat.empty()) {
                // OpenCV 2.4.13: Use CV_BGR2RGB em vez de cv::COLOR_BGR2RGB
                cv::cvtColor(frame_mat, frame_mat, CV_BGR2RGB);

                QImage newFrame((uchar*)frame_mat.data,
                                frame_mat.cols,
                                frame_mat.rows,
                                frame_mat.step,
                                QImage::Format_RGB888);

                // Thread-safe: bloqueia o mutex ao atualizar
                QMutexLocker locker(&frameMutex);
                currentFrame = newFrame.copy();
                locker.unlock();

                qDebug() << "✅ Frame decodificado:" << frame_mat.cols << "x" << frame_mat.rows;

                emit frameReceived();
            } else {
                qWarning() << "❌ OpenCV: Frame vazio após decodificação";
            }
        } catch (const std::exception& e) {
            qWarning() << "❌ OpenCV Exception:" << e.what();
        }
    }
}

QImage UdpFrameReceiver::getCurrentFrame() const
{
    QMutexLocker locker(&frameMutex);
    return currentFrame;
}

// ==================== UdpFrameProvider ====================
UdpFrameProvider::UdpFrameProvider(UdpFrameReceiver *receiver)
    : QQuickImageProvider(QQuickImageProvider::Image)
    , frameReceiver(receiver)
{
}

QImage UdpFrameProvider::requestImage(const QString &id, QSize *size, const QSize &requestedSize)
{
    Q_UNUSED(id);
    Q_UNUSED(requestedSize);

    QImage frame = frameReceiver->getCurrentFrame();

    if (size)
        *size = frame.size();

    return frame;
}

// ==================== UdpFrameClient ====================
UdpFrameClient::UdpFrameClient(QObject *parent)
    : QObject(parent)
{
    m_receiver = new UdpFrameReceiver(this);
    connect(m_receiver, &UdpFrameReceiver::frameReceived,
            this, &UdpFrameClient::onFrameReceived);
}
