import cv2
import os

# Klasör yolları
output_dir = "Dirty-Clothes-Image-Classifications"
not_implemented_dir = os.path.join(output_dir, "not_implemented")
implemented_dir = os.path.join(output_dir, "implemented")

# Klasörlerin var olup olmadığını kontrol et ve oluştur
os.makedirs(not_implemented_dir, exist_ok=True)
os.makedirs(implemented_dir, exist_ok=True)

# Video dosya yolu
video_path = "IMG_2046.mov"  # Buraya video dosya yolunu ekleyin
cap = cv2.VideoCapture(video_path)

# Sayaçlar
not_implemented_count = 0
implemented_count = 0

# ROI seçimi için değişkenler
roi_selected = False
roi = (0, 0, 0, 0)
selecting_no_impl = True  # İlk olarak "no implemented" alanını seçiyoruz

# ROI seçim fonksiyonu
def select_roi(event, x, y, flags, param):
    global roi, roi_selected, selecting_no_impl, not_implemented_count, implemented_count, frame
    
    if event == cv2.EVENT_LBUTTONDOWN:
        roi = (x, y, x, y)
        roi_selected = False
    elif event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:
        roi = (roi[0], roi[1], x, y)
    elif event == cv2.EVENT_LBUTTONUP:
        roi = (roi[0], roi[1], x, y)
        roi_selected = True

        # Seçim tamamlandığında alanı kaydet
        x1, y1, x2, y2 = roi
        cropped_frame = frame[y1:y2, x1:x2]

        # Eğer seçilen alan boş değilse kaydet
        if cropped_frame.size > 0:
            if selecting_no_impl and not_implemented_count < 5:
                # "No implemented" alanını kaydet ve mavi çerçeve ekle
                not_implemented_count += 1
                file_name = f"no_impl_{not_implemented_count}.jpg"
                
                # Mavi çerçeve çiz
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Mavi renk
                
                # Seçilen alanı kaydet
                cv2.imwrite(os.path.join(not_implemented_dir, file_name), cropped_frame)
                print(f"Saved: {file_name} to 'not implemented'")
                
                # 5 adet "no implemented" tamamlandığında "implemented" moduna geç
                if not_implemented_count >= 5:
                    selecting_no_impl = False
            elif not selecting_no_impl:
                # "Implemented" alanını kaydet ve mavi çerçeve ekle
                implemented_count += 1
                file_name = f"impl_{implemented_count}.jpg"
                
                # Mavi çerçeve çiz
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Mavi renk
                
                # Seçilen alanı kaydet
                cv2.imwrite(os.path.join(implemented_dir, file_name), cropped_frame)
                print(f"Saved: {file_name} to 'implemented'")

# Video işlemi için ana döngü
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Sayaçları ekrana yazdır
    text_no_impl = f"No Implemented Count: {not_implemented_count}/5"
    text_impl = f"Implemented Count: {implemented_count}/10"
    cv2.putText(frame, text_no_impl, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    cv2.putText(frame, text_impl, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    # Çerçeveyi göster
    cv2.imshow("Video", frame)
    cv2.setMouseCallback("Video", select_roi)

    # Her 1 ms'de bir kontrol et, seçim tamamlandığında yeni kareye geçer
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break  # İstediğinizde 'q' tuşuna basarak videoyu durdurabilirsiniz

    # Limitlere ulaşıldığında işlemi sonlandır
    if not_implemented_count >= 5 and implemented_count >= 10:
        break

# Video ve pencereyi serbest bırak
cap.release()
cv2.destroyAllWindows()
