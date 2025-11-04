import socket
import numpy as np
import cv2  # NECESSÁRIO para codificar JPEG

class UDPFrameSender:
    def __init__(self, serverIP, serverPORT, jpeg_quality=80):
        """
        Inicializa sender UDP com compressão JPEG.
        
        Args:
            serverIP: IP do servidor (ex: "127.0.0.1")
            serverPORT: Porta UDP (ex: 8383)
            jpeg_quality: Qualidade JPEG 0-100 (padrão: 80)
        """
        print("=" * 50)
        print("🔌 UDP SENDER INIT")
        print("=" * 50)
        
        self.serverIP = serverIP
        self.serverPort = serverPORT
        self.jpeg_quality = jpeg_quality
        self.clientSocket = None
        
        # Tamanho máximo seguro para UDP
        self.MAX_SAFE_UDP_SIZE = 60000

        try:
            self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Aumenta buffer de envio
            self.clientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
            print(f"✅ Socket UDP criado: {serverIP}:{serverPORT}")
            print(f"📊 Qualidade JPEG: {jpeg_quality}%")
            print(f"📦 Tamanho máximo: {self.MAX_SAFE_UDP_SIZE} bytes")
            print("=" * 50 + "\n")
        except Exception as e:
            print(f"❌ Erro ao criar socket: {e}")

    def encodeImage(self, frame):
        """
        Codifica frame OpenCV em JPEG e retorna os bytes.
        
        Args:
            frame: Frame OpenCV (numpy array BGR)
            
        Returns:
            bytes: Frame codificado em JPEG ou None se falhar
        """
        try:
            # CORREÇÃO PRINCIPAL: Codifica em JPEG usando OpenCV
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality]
            result, encoded_frame = cv2.imencode('.jpg', frame, encode_param)
            
            if not result:
                print("❌ Falha ao codificar frame em JPEG")
                return None
            
            # Converte para bytes
            data = encoded_frame.tobytes()
            data_size = len(data)
            
            # Verifica tamanho
            if data_size > self.MAX_SAFE_UDP_SIZE:
                print(f"⚠️ Frame muito grande: {data_size} bytes (max: {self.MAX_SAFE_UDP_SIZE})")
                print("💡 Dica: Reduza jpeg_quality ou a resolução da câmera")
                return None
            
            return data
            
        except Exception as e:
            print(f"❌ Erro ao codificar frame: {e}")
            return None

    def sendFrame(self, frame):
        """
        Codifica E envia frame via UDP (método completo).
        
        Args:
            frame: Frame OpenCV (numpy array BGR)
            
        Returns:
            bool: True se enviado com sucesso, False caso contrário
        """
        # Codifica em JPEG
        encoded_data = self.encodeImage(frame)
        
        if encoded_data is None:
            return False
        
        # Envia via UDP
        return self.sendEncodedImage(encoded_data)

    def sendEncodedImage(self, encodedData):
        """
        Envia dados já codificados via UDP.
        
        Args:
            encodedData: Bytes para enviar
            
        Returns:
            bool: True se enviado, False caso contrário
        """
        try:
            if self.clientSocket is None:
                print("❌ Socket não inicializado")
                return False
            
            bytes_sent = self.clientSocket.sendto(encodedData, (self.serverIP, self.serverPort))
            
            # Verifica se enviou tudo
            if bytes_sent != len(encodedData):
                print(f"⚠️ Enviado parcial: {bytes_sent}/{len(encodedData)} bytes")
                return False
            
            return True
            
        except socket.error as e:
            print(f"❌ Erro de socket ao enviar: {e}")
            return False
        except Exception as e:
            print(f"❌ Erro ao enviar dados: {e}")
            return False

    def closeSocketConnection(self):
        """Fecha conexão do socket."""
        try:
            if self.clientSocket:
                self.clientSocket.close()
                print("✅ Conexão fechada")
        except Exception as e:
            print(f"⚠️ Erro ao fechar socket: {e}")

    def __del__(self):
        """Destrutor: fecha socket automaticamente."""
        self.closeSocketConnection()


# Teste standalone
if __name__ == "__main__":
    import time
    
    print("\n🧪 TESTE DO UDP SENDER")
    print("=" * 50 + "\n")
    
    # Cria frame de teste (imagem preta com texto)
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(test_frame, "UDP TEST FRAME", (150, 240), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
    
    # Cria sender
    sender = UDPFrameSender("127.0.0.1", 8383, jpeg_quality=80)
    
    if sender.clientSocket is None:
        print("❌ Falha ao criar sender")
        exit(1)
    
    print("📤 Enviando 10 frames de teste...\n")
    
    success_count = 0
    for i in range(10):
        # Atualiza texto no frame
        frame = test_frame.copy()
        cv2.putText(frame, f"Frame #{i+1}", (220, 300), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Envia
        if sender.sendFrame(frame):
            success_count += 1
            print(f"✅ Frame {i+1}/10 enviado")
        else:
            print(f"❌ Frame {i+1}/10 FALHOU")
        
        time.sleep(0.1)  # 100ms entre frames
    
    print(f"\n📊 Resultado: {success_count}/10 frames enviados com sucesso")
    
    sender.closeSocketConnection()
    print("\n✅ Teste concluído\n")
