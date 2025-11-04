import cv2
import mediapipe as mp
import json
import socket
import time

class HandTracker:
    def __init__(self, cameraDeviceID=0, showCamera=True):
        """
        Hand Tracker com MediaPipe + envio UDP dos landmarks.
        
        Args:
            cameraDeviceID: ID da câmera
            showCamera: Mostrar janela de debug
        """
        print("=" * 60)
        print("🖐️  HAND TRACKER - MediaPipe + UDP")
        print("=" * 60)
        
        self.deviceCamID = cameraDeviceID
        self.debugCamera = showCamera
        
        # Inicializa MediaPipe Hands
        print("\n🤖 Inicializando MediaPipe...")
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Configurações do detector
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,              # Detecta até 2 mãos
            min_detection_confidence=0.7,  # Confiança mínima para detecção
            min_tracking_confidence=0.5    # Confiança mínima para tracking
        )
        
        print("✅ MediaPipe Hands inicializado")
        print(f"   • Máximo de mãos: 2")
        print(f"   • Confiança de detecção: 0.7")
        print(f"   • Confiança de tracking: 0.5")
        
        # Socket UDP para enviar landmarks
        print("\n🔌 Configurando UDP...")
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_ip = "127.0.0.1"
        self.server_port = 8384  # Porta diferente do vídeo
        
        print(f"✅ UDP configurado: {self.server_ip}:{self.server_port}")
        
        # Estatísticas
        self.frame_count = 0
        self.hands_detected_count = 0
        self.packets_sent = 0
        
    def process_hands(self, frame):
        """
        Processa frame e detecta mãos.
        
        Returns:
            tuple: (frame_anotado, dados_json)
        """
        # Converte BGR para RGB (MediaPipe usa RGB)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Processa frame
        results = self.hands.process(frame_rgb)
        
        # Prepara dados para enviar
        hands_data = {
            "timestamp": time.time(),
            "frame_number": self.frame_count,
            "hands_detected": 0,
            "hands": []
        }
        
        # Se detectou mãos
        if results.multi_hand_landmarks:
            hands_data["hands_detected"] = len(results.multi_hand_landmarks)
            self.hands_detected_count += 1
            
            # Para cada mão detectada
            for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Pega informação sobre qual mão (esquerda/direita)
                handedness = results.multi_handedness[hand_idx].classification[0]
                hand_label = handedness.label  # "Left" ou "Right"
                hand_score = handedness.score
                
                # Extrai landmarks (21 pontos)
                landmarks = []
                for landmark in hand_landmarks.landmark:
                    landmarks.append({
                        "x": landmark.x,      # Normalizado 0-1
                        "y": landmark.y,      # Normalizado 0-1
                        "z": landmark.z,      # Profundidade relativa
                        "visibility": landmark.visibility
                    })
                
                # Adiciona mão aos dados
                hands_data["hands"].append({
                    "hand_index": hand_idx,
                    "label": hand_label,
                    "confidence": hand_score,
                    "landmarks": landmarks
                })
                
                # Desenha landmarks no frame (para debug)
                if self.debugCamera:
                    self.mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style()
                    )
                    
                    # Adiciona texto com label da mão
                    h, w, _ = frame.shape
                    cx = int(hand_landmarks.landmark[0].x * w)
                    cy = int(hand_landmarks.landmark[0].y * h)
                    cv2.putText(frame, f"{hand_label} ({hand_score:.2f})", 
                               (cx - 50, cy - 20),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                               (0, 255, 0), 2)
        
        return frame, hands_data
    
    def send_hand_data(self, hands_data):
        """
        Envia dados das mãos via UDP (JSON).
        
        Args:
            hands_data: Dicionário com dados das mãos
            
        Returns:
            bool: True se enviado com sucesso
        """
        try:
            # Converte para JSON
            json_data = json.dumps(hands_data)
            json_bytes = json_data.encode('utf-8')
            
            # Verifica tamanho (UDP tem limite)
            if len(json_bytes) > 60000:
                print(f"⚠️ Dados muito grandes: {len(json_bytes)} bytes")
                return False
            
            # Envia via UDP
            self.udp_socket.sendto(json_bytes, (self.server_ip, self.server_port))
            self.packets_sent += 1
            return True
            
        except Exception as e:
            print(f"❌ Erro ao enviar dados: {e}")
            return False
    
    def run(self):
        """Inicia o loop de captura e detecção."""
        print(f"\n📷 Abrindo câmera {self.deviceCamID}...")
        
        # Abre câmera
        cap = cv2.VideoCapture(self.deviceCamID, cv2.CAP_DSHOW)
        
        if not cap.isOpened():
            print("❌ ERRO: Não foi possível abrir a câmera!")
            return
        
        # Configurações
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"✅ Câmera aberta: {width}x{height}")
        print(f"\n{'='*60}")
        print("🚀 INICIANDO DETECÇÃO DE MÃOS")
        print("⏸️  Pressione ESC para parar")
        print("📊 Estatísticas a cada 30 frames")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                
                if not ret:
                    print("⚠️ Falha ao capturar frame")
                    break
                
                self.frame_count += 1
                
                # Processa mãos
                annotated_frame, hands_data = self.process_hands(frame)
                
                # Envia dados via UDP
                self.send_hand_data(hands_data)
                
                # Estatísticas a cada 30 frames
                if self.frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    fps = self.frame_count / elapsed if elapsed > 0 else 0
                    detection_rate = (self.hands_detected_count / self.frame_count * 100) if self.frame_count > 0 else 0
                    
                    print(f"📊 Frames: {self.frame_count} | "
                          f"Detecções: {self.hands_detected_count} | "
                          f"Taxa: {detection_rate:.1f}% | "
                          f"FPS: {fps:.1f} | "
                          f"Pacotes: {self.packets_sent}")
                
                # Mostra janela de debug
                if self.debugCamera:
                    # Adiciona informações na tela
                    info_frame = annotated_frame.copy()
                    cv2.putText(info_frame, f"Frames: {self.frame_count}", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(info_frame, f"Maos detectadas: {hands_data['hands_detected']}", 
                               (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
                    cv2.imshow('Hand Tracking - Pressione ESC', info_frame)
                    
                    if cv2.waitKey(1) & 0xFF == 27:  # ESC
                        print("\n⏹️  ESC pressionado - Encerrando...")
                        break
                        
        except KeyboardInterrupt:
            print("\n⏹️  Interrompido (Ctrl+C)")
            
        except Exception as e:
            print(f"\n❌ ERRO: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            # Cleanup
            print("\n" + "=" * 60)
            print("🧹 LIMPANDO RECURSOS")
            print("=" * 60)
            
            cap.release()
            cv2.destroyAllWindows()
            self.hands.close()
            self.udp_socket.close()
            
            # Estatísticas finais
            print(f"\n📈 ESTATÍSTICAS FINAIS:")
            print(f"   • Total de frames: {self.frame_count}")
            print(f"   • Frames com mãos detectadas: {self.hands_detected_count}")
            print(f"   • Pacotes UDP enviados: {self.packets_sent}")
            
            if self.frame_count > 0:
                detection_rate = (self.hands_detected_count / self.frame_count * 100)
                print(f"   • Taxa de detecção: {detection_rate:.1f}%")
            
            print("\n✅ Programa encerrado\n")


# Execução
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("HAND TRACKING - MediaPipe + UDP Sender")
    print("=" * 60 + "\n")
    
    try:
        tracker = HandTracker(cameraDeviceID=0, showCamera=True)
        tracker.run()
        
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
