


# Archlinux



**System**
- Zen Kernel
- Base Devel
- Z-Shell
- Yay
- Gnome
- GDM



**Extensions**
- System Monitor
- Dash to Dock
- Dynamic Panel
- Remove Arrows



**Apps**
- Firefox
- Chromium
- Simplenote
- Trello
- Notion
- Figma
- Darktable
- PhotoQT
- VScode
- Repl.it
- Tilix
- Slack
- Discord


## Post-Install


**Particoes**
- sudo fdisk -l
- sudo blkid
- sudo vim /etc/fstab


**Git / Go / tlp**
- sudo pacman -S git go tlp
- sudo tlp start
- sudo tlp-stat


**Yay**
- git clone https://aur.archlinux.org/yay.git
- cd yay
- makepkg -si
- sudo pacman -Rnus go



**oh-my-zsh**
- sh -c "$(wget https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh -O -)"
- git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
- git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
- vim ~/.zshrc
- plugins=(
    archlinux
    git
    colored-man-pages
    zsh-autosuggestions
    zsh-syntax-highlighting
    history-substring-search
)



**Gnome**
- yay -Rnus gnome
- yay -S gnome ( *1 7 9 17 33 52* )
- yay -S gnome-keyring


**Extensions**
- yay -S gnome-shell-extension-system-monitor-git gnome-shell-extension-remove-dropdown-arrows gnome-shell-extension-dash-to-dock



**Symlinks / Home**
- ln -s /mnt/...
- .themes 
- .icons 
- .fonts 
- .oh-my-zsh
- .zshrc
- .zsh_history 
- .vim
- .vimrc
- .vscode 
- .gitconfig
- gtk.css



**Themes / Icons**
- Juno-Master-EA
- Paper-EA



**Apps** 
- yay -S firefox-developer-edition chromium trello-git simplenote-electron-bin notion-app figma-linux darktable-git photoqt visual-studio-code-bin replit-desktop-bin tilix slack-desktop discord-canary gnome-tweaks



**RVM / Ruby**
- gpg --keyserver hkp://pool.sks-keyservers.net --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3 7D2BAF1CF37B13E2069D6956105BD0E739499BDB
- curl -sSL https://get.rvm.io | bash -s stable --ruby
- vim .zshrc
- source $HOME/.rvm/scripts/rvm



**Jekyll**
- gem install bundler jekyll
- jekyll new (nome-do-projeto)
- bundle exec jekyll serve



**emersonalmeida.github.io**
- git clone https://github.com/emersonalmeida/emersonalmeida.github.io



---



### xorg

**Brightness**
- xrandr -q | grep ' connected' | head -n 1 | cut -d ' ' -f1
- xrandr --output DVI-D-0 --brightness 0.5

**Touchpad**
- sudo vim /etc/X11/xorg.conf.d/90-touchpad.conf
- Section "InputClass"
        Identifier "touchpad"
        MatchIsTouchpad "on"
        Driver "libinput"
        Option "Tapping" "on"
        Option "TappingButtonMap" "lrm"
        Option "NaturalScrolling" "on"
        Option "ScrollMethod" "twofinger"
EndSection

**Teclado***
- sudo vim /etc/X11/xorg.conf.d/10-evdev.conf
- Section “InputClass”
    Identifier “evdev keyboard catchall”
    MatchIsKeyboard “on”
    MatchDevicePath “/dev/input/event*”
    Driver “evdev”
    Option “XkbLayout” “br”
    Option “XkbVariant” “abnt2"
EndSection 
- ou
- sudo localectl set-x11-keymap br abnt2

### i3

**Montar Particao**
- sudo fdisk -l
- sudo blkid
- sudo vim /etc/fstab
- UUID - /mnt/server - ntfs - defaults - 0 0

**i3 config**
- vim ~/.config/i3/config
- for_window [class="^.*"] border pixel 0
- gaps inner 32
- gaps outer 32

**Nitrogen Wallpaper**
- sudo pacman -S nitrogen
- vim ~/.config/i3/config
- exec --no-startup-id nitrogen --restore

**Ranger**
- sudo pacman -S ranger w3m imlib2 
- sudo vim ~/.config/ranger/rc.conf 
- set preview_images true

**themes**
- sudo pacman -S lxappearance

**Apps**
- Dmenu
- Albert
- Ranger

