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

# Sound - Over Ampification
gsettings set org.gnome.desktop.sound allow-volume-above-100-percent 'true'

# Disable gnome animation
gsettings reset org.gnome.desktop.interface enable-animations
gsettings set org.gnome.desktop.interface enable-animations false
gsettings set org.gnome.shell.extensions.dash-to-dock animate-show-apps false
gsettings reset org.gnome.shell.extensions.dash-to-dock animate-show-apps

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

# ~/.config/gtk-3.0/gtk.css
VteTerminal,
TerminalScreen,
vte-terminal {
    padding: 32px;
    -VteTerminal-inner-border: 32px;
}

# Custom
yay -S base-devel
yay -S zorin-icon-themes gnome-shell-extension-blur-my-shell gnome-shell-extension-caffeine  gnome-shell-extension-custom-hot-corners-extended-git gnome-shell-extension-dash-to-dock gnome-shell-extension-gnome-ui-tune gnome-shell-extension-pop-shell-git  gnome-shell-extension-todotxt-git gnome-shell-extension-vertical-workspaces-git --needed --noconfirm

# Terminal Font
yay -S terminus-font && sudo gedit /etc/vconsole.conf 
KEYMAP=br-abnt2
FONT=ter-p32n
FONT_MAP=8859-2

# key's
// para criar as chaves precisa do comando keygen quem faz parte do pacote OpenSSH, quem nao vem instalado por padrao no archlinux
yay -S openssh
ssh-keygen -o -a 100 -t ed25519 -f ~/.ssh/id_ed25519 -C "emersonalmeida@live.com"
cat ~/.ssh/id_ed25519.pub
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# token
git config --global credential.helper cache
git config --global --unset crendential.helper

# git
git config --global user.name "Emerson Almeida"
git config --global user.email emersonalmeida@live.com
git config --global core.editor nano
git config --global --add safe.directory /mnt/sda4/git/emersonalmeida.github.io
git config -list
git clone url
git init
git status
git add .
git commit -m "msg"
git log
git checkout chavedocommit
git remote add origin url-repositorio
git push -u origin main
git pull
git pull origin main

# wacom
echo "# Adicionando Scroll Wacom Pen"
echo "## xsetwacom set "Wacom Intuos BT S Pen stylus" Button 2 "pan""
echo "### xsetwacom set "Wacom Intuos BT S Pen stylus" "PanScrollThreshold" 200"
xsetwacom set "Wacom Intuos BT S Pen stylus" Button 2 "pan" 
xsetwacom set "Wacom Intuos BT S Pen stylus" "PanScrollThreshold" 200 
echo "#### Concluído ### "

