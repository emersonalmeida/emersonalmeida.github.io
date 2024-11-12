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

# Gnome animation
gsettings set org.gnome.desktop.interface enable-animations false
gsettings reset org.gnome.desktop.interface enable-animations
gsettings set org.gnome.shell.extensions.dash-to-dock animate-show-apps false
gsettings reset org.gnome.shell.extensions.dash-to-dock animate-show-apps

# Disable extension
gsettings set org.gnome.shell disable-user-extensions true
gsettings set org.gnome.shell disable-user-extensions false
dconf write /org/gnome/shell/extensions/enabled true
dconf write /org/gnome/shell/extensions/enabled false

# Default open folder in nautilus
xdg-mime default org.gnome.Nautilus.desktop inode/directory

# Oh My ZSH
sh -c "$(wget https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh -O -)"
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting 
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions

# ZSH Config
nano .zshrc
ZSH_THEME="minimal"
plugins=(
    git
    archlinux
    colored-man-pages
    zsh-autosuggestions
    zsh-syntax-highlighting
    history-substring-search
)

# terminal padding
echo "VteTerminal,
TerminalScreen,
vte-terminal {
    padding: 32px;
    -VteTerminal-inner-border: 32px;
}" >> ~/.config/gtk-3.0/gtk.css


# extensoes
yay -S base-devel --noconfirm --needed && yay -S zorin-icon-themes gnome-shell-extension-blur-my-shell gnome-shell-extension-caffeine  gnome-shell-extension-custom-hot-corners-extended-git gnome-shell-extension-dash-to-dock gnome-shell-extension-gnome-ui-tune gnome-shell-extension-pop-shell-git  gnome-shell-extension-todotxt-git gnome-shell-extension-vertical-workspaces-git --needed --noconfirm

# Terminal Font
yay -S terminus-font && sudo gedit /etc/vconsole.conf 
KEYMAP=br-abnt2
FONT=ter-p32n
FONT_MAP=8859-2

echo "VteTerminal,
TerminalScreen,
vte-terminal {
    padding: 32px;
    -VteTerminal-inner-border: 32px;
} >> " ~/.config/gtk-3.0/gtk.css

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

# pacman 
-S (install): Instala pacotes. Ex: sudo pacman -S firefox
-Ss (search): Busca por pacotes nos repositórios. Ex: sudo pacman -Ss firefox
-Ssi (search and install): Combina busca e instalação. Ex: sudo pacman -Ssi htop
-Sy (sync): Atualiza o sistema e instala novos pacotes (se houverem).
-Syu (sync upgrade): Atualiza o sistema e instala todas as atualizações disponíveis (incluindo pacotes AUR, se habilitado).
-R (remove): Remove pacotes instalados. Ex: sudo pacman -R firefox
-Rs (remove with dependencies): Remove pacotes instalados e todas as dependências que não são necessárias para outros pacotes.
-Rncs (remove, clean, sync): Remove pacotes instalados, dependências desnecessárias e limpa o cache do pacman (combina -R, -Rs e -Sc).
-Rdd (remove orphans): Remove pacotes órfãos (pacotes instalados que não possuem dependências de outros pacotes).
-Sc (check): Verifica a integridade dos pacotes instalados (cache).
-Scc (clean): Limpa o cache do pacman.
-Q (query): Lista todos os pacotes instalados.
-Qi (query information): Mostra informações detalhadas de um pacote instalado. Ex: sudo pacman -Qi firefox
-Qe (query explicit): Lista pacotes explicitamente instalados (não inclui dependências).
-Qm (query marked): Lista pacotes marcados para atualização.
-Qem (query error): Lista pacotes com dependências conflitantes.
-Qt (query available): Lista todos os pacotes disponíveis nos repositórios (igual a pacman -Ss).
-Qtt (query tag): Mostra a tag de versão de um pacote nos repositórios. Ex: sudo pacman -Qtt firefox
-Qet (query explicit tree): Mostra todas as dependências de um pacote. Ex: sudo pacman -Qet firefox
-Qettn (query explicit tree no dependencies): Mostra as dependências obrigatórias de um pacote (não opcionais).
-Qettm (query explicit tree user modified): Mostra as dependências feitas pelo próprio usuário (marcadas manualmente).

# Gerenciamento de Usuários e Grupos:
useradd: Cria um novo usuário.
passwd: Define ou altera a senha de um usuário.
deluser: Remove um usuário.
groupadd: Cria um novo grupo.
groupmod: Modifica um grupo existente.
delgroup: Remove um grupo.
usermod: Modifica um usuário existente.
groups: Mostra os grupos aos quais um usuário pertence.
sudoers: Edita o arquivo sudoers para conceder privilégios administrativos a usuários.

# permissões
permissão, binário, decimal
--- 000 0
--x 001 1
-w- 010 2
-wx 011 3
r-- 100 4
r-x 101 5
rw- 110 6
rwx 111 7
u = user (dono)
g = group (grupo)
o = others (público)
a = all (todos)
drwxr-xr-x - dir, read, write, execute
chmod +x (permissão de execução)
chmod u+x (execução somente para usuario)
chmod 777 = chmod ugo+rwx (todas as permissões)

# Configuração do Sistema:
pacman -S dhcpcd: Instala e configura o dhcpcd para gerenciamento automático de IP.
systemctl: Gerencia serviços do sistema (systemd).
hostnamectl: Configura o nome de host do sistema.
locale-gen: Gera arquivos de localidade para diferentes idiomas.
locale-config: Configura o idioma e a codificação do sistema.
timedatectl: Configura a data, hora e fuso horário do sistema.
mkinitcpio: Gera os arquivos initramfs necessários




