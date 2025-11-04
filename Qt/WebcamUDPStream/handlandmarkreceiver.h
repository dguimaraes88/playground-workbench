#ifndef HANDLANDMARKRECEIVER_H
#define HANDLANDMARKRECEIVER_H

#include <QObject>
#include <QUdpSocket>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QVariantList>
#include <QVariantMap>

class HandLandmarkReceiver : public QObject
{
    Q_OBJECT
    Q_PROPERTY(int handsDetected READ handsDetected NOTIFY handsDataChanged)
    Q_PROPERTY(QVariantList hands READ hands NOTIFY handsDataChanged)

public:
    explicit HandLandmarkReceiver(QObject *parent = nullptr);

    int handsDetected() const { return m_handsDetected; }
    QVariantList hands() const { return m_hands; }

signals:
    void handsDataChanged();
    void newHandData(int handsCount);

private slots:
    void processPendingDatagrams();

private:
    QUdpSocket *udpSocket;
    int m_handsDetected;
    QVariantList m_hands;

    void parseHandData(const QByteArray &data);
};

#endif // HANDLANDMARKRECEIVER_H
