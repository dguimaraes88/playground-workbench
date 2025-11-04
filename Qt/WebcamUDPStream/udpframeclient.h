#ifndef UDPFRAMECLIENT_H
#define UDPFRAMECLIENT_H

#include <QObject>
#include <QUdpSocket>
#include <QImage>
#include <QByteArray>
#include <QQuickImageProvider>
#include <QMutex>
#include <opencv2/opencv.hpp>

// Classe 1: Gerencia o socket UDP e recebe frames (herda de QObject)
class UdpFrameReceiver : public QObject
{
    Q_OBJECT

public:
    explicit UdpFrameReceiver(QObject *parent = nullptr);
    QImage getCurrentFrame() const;

signals:
    void frameReceived();

private slots:
    void processPendingDatagrams();

private:
    QUdpSocket *udpSocket;
    QImage currentFrame;
    mutable QMutex frameMutex; // Proteção thread-safe
};

// Classe 2: Fornece imagens ao QML (herda de QQuickImageProvider)
class UdpFrameProvider : public QQuickImageProvider
{
public:
    explicit UdpFrameProvider(UdpFrameReceiver *receiver);
    QImage requestImage(const QString &id, QSize *size, const QSize &requestedSize) override;

private:
    UdpFrameReceiver *frameReceiver;
};

// Classe 3: Wrapper QObject opcional para expor ao QML (se necessário)
class UdpFrameClient : public QObject
{
    Q_OBJECT
    Q_PROPERTY(QString imageSource READ imageSource NOTIFY imageSourceChanged)

public:
    explicit UdpFrameClient(QObject *parent = nullptr);
    QString imageSource() const { return "image://udp/currentFrame"; }
    UdpFrameReceiver* receiver() { return m_receiver; }

signals:
    void imageSourceChanged();

private slots:
    void onFrameReceived() { emit imageSourceChanged(); }

private:
    UdpFrameReceiver *m_receiver;
};

#endif // UDPFRAMECLIENT_H
