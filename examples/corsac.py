import os

import archinstall
from archinstall import SysCommand

SysCommand('mkdir /mnt/efi')
SysCommand('mkdir /mnt/root')
SysCommand('mkdir /mnt/usb')

# TODO mount usb drive

targetDisk = archinstall.BlockDevice(path=input("Enter disk to install to: "))
hostname = input('Enter hostname: ')
keyfile = '/mnt/usb/keyfile_' + hostname

disk_password = os.urandom(2048)

with archinstall.Filesystem(targetDisk, archinstall.GPT) as fs:
	fs.use_entire_disk(root_filesystem_type="crypto_LUKS", efi_size='200MiB', efi_mount_point='/mnt/efi')
	root_partition = fs.find_partition('/')
	root_partition.encrypt(password=disk_password, key_file=keyfile)

with archinstall.luks2(root_partition, 'cryptlvm', disk_password) as crypt_container:
	SysCommand('pvcreate ' + crypt_container.path)
	SysCommand('vgcreate vgroot ' + crypt_container.path)
	SysCommand('lvcreate -L 8G vgroot -n swap')
	SysCommand('lvcreate -l 100%FREE vgroot -n root')
	SysCommand('mkswap /dev/vgroot/swap')
	SysCommand('swapon /dev/vgroot/swap')
	SysCommand('mkfs.ext4 /dev/vgroot/root')
	SysCommand('mount /dev/vgroot/root /mnt/root')

#with archinstall.Installer('/mnt/root') as installation:
#	installation.set_hostname(hostname)

