# OpenCV 2.4.13 Configuration
COMPONENT = opencv
OPENCVDIR = $$PWD

# Include directories
INCLUDEPATH += $$OPENCVDIR/inc/

# Required libraries for OpenCV 2.4.13
# IMPORTANTE: imgcodecs está integrado em highgui na versão 2.4.x
LIBS += $$PWD/lib/opencv_core2413.lib \
        $$PWD/lib/opencv_imgproc2413.lib \
        $$PWD/lib/opencv_highgui2413.lib

# Bibliotecas opcionais (descomente se necessário)
# LIBS += $$PWD/lib/opencv_ml2413.lib \
#         $$PWD/lib/opencv_video2413.lib \
#         $$PWD/lib/opencv_contrib2413.lib

# Build configuration
BUILD_TYPE = build
DESTDIR = $$shadowed(../$$BUILD_TYPE)

# DLL deployment
opencv.files = $$PWD/dll/*.dll
opencv.path  = $$DESTDIR
INSTALLS += opencv

# Copia DLLs para o diretório de saída (Windows)
win32 {
    QMAKE_POST_LINK += $$quote(xcopy /Y /D \"$$shell_path($$PWD/dll/*.dll)\" \"$$shell_path($$DESTDIR)\" 2>nul)
}
