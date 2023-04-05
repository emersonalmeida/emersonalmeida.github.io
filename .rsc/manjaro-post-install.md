# Init
sudo systemctl status fstrim.timer
sudo pacman-mirrors --fasttrack
sudo pacman -Sy
sudo pacman -Syyu

# Remove Manjaro Branding
sudo pacman -Rdd manjaro-artwork grub-theme-manjaro manjaro-gdm-branding && sudo pacman -Rncs zsh

# Terminal
sudo pacman -S yay tilix zsh

# Tilix Height 
gsettings set com.gexperts.Tilix.Settings quake-height-percent 100

# Oh My ZSH
sh -c "$(wget https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh -O -)"
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting 
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions

# ZSH Config
gedit .zshrc
ZSH_THEME="minimal"
plugins=(
    git
    archlinux
    colored-man-pages
    zsh-autosuggestions
    zsh-syntax-highlighting
    history-substring-search
)

# TLP
sudo pacman -S tlp && sudo tlp start && sudo tlp-stat

# Terminal Font
yay -S terminus-font && sudo gedit /etc/vconsole.conf 
KEYMAP=br-abnt2
FONT=ter-p32n
FONT_MAP=8859-2


# Extensions
yay -S gnome-shell-extension-alphabetical-grid-extension gnome-shell-extension-blur-my-shell gnome-shell-extension-caffeine-git gnome-shell-extension-custom-hot-corners-extended-git gnome-shell-extension-dash-to-dock gnome-shell-extension-gnome-ui-tune-git gnome-shell-extension-pop-shell gnome-shell-extension-system-monitor-git gnome-shell-extension-vertical-workspaces-git
 

# Apps

