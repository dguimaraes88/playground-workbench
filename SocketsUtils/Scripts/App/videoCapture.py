import cv2
import time
from udpFrameSender import UDPFrameSender
from handTracker import HandTracker

class VideoCapture:
    def __init__(self, cameraDeviceID=0, showCamera=True, jpeg_quality=70):
        """
        Inicializa captura de vídeo com streaming UDP.
        
        Args:
            cameraDeviceID: ID da câmera (0, 1, 2...)
            showCamera: True para mostrar janela de debug
        """
        print("=" * 50)
        print("📹 VIDEO CAPTURE - INICIANDO")
        print("=" * 50)
        
        self.deviceCamID = cameraDeviceID
        self.debugCamera = showCamera
        
        # Cria sender UDP (SEM jpeg_quality - compatível com sua classe)
        print(f"\n🔌 Conectando UDP...")
        self.udpObj = UDPFrameSender("127.0.0.1", 8383)
        self.handTrackerObj = HandTracker(cameraDeviceID=0, showCamera=False)
        
        # Contadores
        self.frame_count = 0
        self.sent_count = 0
        self.failed_count = 0
        
    def initVideoCapture(self):
        """Inicia loop de captura e envio de frames."""
        print(f"\n📷 Abrindo câmera {self.deviceCamID}...")
        
        # Abre câmera
        self.cap = cv2.VideoCapture(self.deviceCamID, cv2.CAP_DSHOW)
        
        if not self.cap.isOpened():
            print("❌ ERRO: Não foi possível abrir a câmera!")
            print("💡 Verifique se a câmera está conectada e não está em uso")
            return
        
        # Configurações da câmera (opcional - ajuste conforme necessário)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Informações da câmera
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        
        print(f"✅ Câmera aberta com sucesso!")
        print(f"📐 Resolução: {width}x{height}")
        print(f"🎬 FPS configurado: {fps}")
        print(f"\n{'='*50}")
        print("🚀 INICIANDO STREAMING")
        print("⏸️  Pressione ESC para parar")
        print(f"{'='*50}\n")
        
        try:
            start_time = time.time()
            
            while self.cap.isOpened():
                ret, frame = self.cap.read()
                # Processa mãos
                frame = cv2.flip(frame,1)
                _, hands_data = self.handTrackerObj.process_hands(frame)
                
                # Envia dados via UDP
                self.handTrackerObj.send_hand_data(hands_data)
                
                if not ret:
                    print("⚠️ Falha ao capturar frame da câmera")
                    break
                
                self.frame_count += 1
                
                # ENVIA O FRAME VIA UDP
                if self.udpObj.sendFrame(frame):
                    self.sent_count += 1
                else:
                    self.failed_count += 1
                    # Mostra erro apenas nos primeiros 5 ou a cada 100
                    if self.failed_count <= 5 or self.failed_count % 100 == 0:
                        print(f"⚠️ Falha ao enviar frame #{self.frame_count}")
                
                # Estatísticas a cada 30 frames (~1 segundo)
                if self.frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    fps_real = self.frame_count / elapsed if elapsed > 0 else 0
                    success_rate = (self.sent_count / self.frame_count * 100) if self.frame_count > 0 else 0
                    
                    print(f"📊 Frames: {self.frame_count} | "
                          f"Enviados: {self.sent_count} | "
                          f"Falhas: {self.failed_count} | "
                          f"Taxa: {success_rate:.1f}% | "
                          f"FPS: {fps_real:.1f}")
                
                # Debug: Mostra janela com o vídeo
                if self.debugCamera:
                    # Adiciona texto de status no frame
                    frame_display = frame.copy()
                    cv2.putText(frame_display, 
                               f"Frames: {self.frame_count} | Enviados: {self.sent_count}", 
                               (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 
                               0.7, 
                               (0, 255, 0), 
                               2)
                    
                    cv2.imshow('CAMERA - Pressione ESC para sair', frame_display)
                    
                    # ESC para sair
                    if cv2.waitKey(1) & 0xFF == 27:
                        print("\n⏹️  ESC pressionado - Encerrando...")
                        break
                        
        except KeyboardInterrupt:
            print("\n⏹️  Interrompido pelo usuário (Ctrl+C)")
            
        except Exception as e:
            print(f"\n❌ ERRO DURANTE CAPTURA: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            # Cleanup
            print("\n" + "=" * 50)
            print("🧹 LIMPANDO RECURSOS")
            print("=" * 50)
            
            self.cap.release()
            cv2.destroyAllWindows()
            self.udpObj.close()
            
            # Estatísticas finais
            print(f"\n📈 ESTATÍSTICAS FINAIS:")
            print(f"   • Total de frames capturados: {self.frame_count}")
            print(f"   • Frames enviados com sucesso: {self.sent_count}")
            print(f"   • Frames com falha: {self.failed_count}")
            
            if self.frame_count > 0:
                success_rate = (self.sent_count / self.frame_count * 100)
                print(f"   • Taxa de sucesso: {success_rate:.1f}%")
            
            print("\n✅ Programa encerrado\n")


# Execução principal
if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("UDP VIDEO STREAMING - PYTHON SENDER")
    print("=" * 50 + "\n")
    
    # Configuração
    CAMERA_ID = 0          # ID da câmera (0 = padrão)
    SHOW_WINDOW = False     # Mostrar janela de preview
    JPEG_QUALITY = 70      # Qualidade JPEG (50-90 recomendado)
    
    try:
        # Cria e inicia captura
        video = VideoCapture(
            cameraDeviceID=CAMERA_ID,
            showCamera=SHOW_WINDOW,
            jpeg_quality=JPEG_QUALITY
        )
        
        # Inicia streaming
        video.initVideoCapture()
        
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
