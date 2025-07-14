# Maintainer: Your Name <your.email@example.com>
pkgname=hel-sys-manager
pkgver=1.0.0
pkgrel=1
pkgdesc="A system manager tool for Linux developed by Helwan Linux community"
arch=('any')
url="https://github.com/helwan-linux/helwan-system-manager"
license=('GPL3')
depends=('python' 'python-pyqt5' 'python-requests')
makedepends=('unzip')
source=("$pkgname-$pkgver.zip::$url/archive/refs/heads/main.zip")
sha256sums=('SKIP')

build() {
  # انتقل إلى المجلد الرئيسي للمشروع بعد فك الضغط.
  # هذا هو المجلد الذي يحتوي على README.md ومجلد src.
  cd "$srcdir/helwan-system-manager-main/hel-sys-manager"
  echo "Nothing to build"
}

package() {
  # انتقل إلى المجلد الرئيسي للمشروع بعد فك الضغط.
  cd "$srcdir/helwan-system-manager-main/hel-sys-manager"

  # نسخ مجلد src بالكامل، والذي يحتوي على جميع ملفات التطبيق (بما في ذلك main.py و hel-sys-manager.desktop)
  install -d "$pkgdir/usr/share/$pkgname"
  cp -r src "$pkgdir/usr/share/$pkgname/"

  # إنشاء مجلد applications قبل تثبيت ملف .desktop
  install -d "$pkgdir/usr/share/applications/"

  # تثبيت ملف .desktop بعد تعديله.
  # لاحظ أننا نشير إلى 'src/hel-sys-manager.desktop' لأن الملف موجود داخل مجلد src.
  sed \
    -e 's|^Exec=hel-sys-manager|Exec=python3 /usr/share/hel-sys-manager/src/main.py|' \
    -e 's|^Icon=hel-sys-manager|Icon=hel-sys-manager|' \
    src/hel-sys-manager.desktop > "$pkgdir/usr/share/applications/hel-sys-manager.desktop"

  # تثبيت أيقونة التطبيق.
  # الأيقونة موجودة في src/assets/icons/app_icon.png
  install -Dm644 src/assets/icons/app_icon.png "$pkgdir/usr/share/icons/hicolor/scalable/apps/hel-sys-manager.png"

  # عمل symlink لتشغيل البرنامج.
  # هذا الـ symlink يشير إلى main.py داخل مجلد src المثبت.
  install -d "$pkgdir/usr/bin"
  ln -s "/usr/share/$pkgname/src/main.py" "$pkgdir/usr/bin/hel-sys-manager"

  # صلاحيات تشغيل للـ main.py.
  chmod +x "$pkgdir/usr/share/$pkgname/src/main.py"
}
