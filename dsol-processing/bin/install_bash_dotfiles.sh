#!/bin/bash

# Install the new .bashrc and .bash_profile files in the user's home
# directory, but keeping any pre-existing ones.

DATE=`date +"%Y-%m-%d-%H:%M"`

# If the user already has a .login for (t)csh, copy it out of the way.
if [ -f ~/.login ]
then
    cp ~/.login ~/.login.${DATE}
fi

# This is for 
cp /packages/dsol/etc/dotfiles/dot_login ~/.login

if [ -f ~/.bashrc ]
then
    cp ~/.bashrc ~/.bashrc.${DATE}
fi

cp /packages/dsol/etc/dotfiles/bashrc ~/.bashrc

if [ -f ~/.bash_profile ]
then
    cp ~/.bash_profile ~/.bash_profile.${DATE}
fi

cp /packages/dsol/etc/dotfiles/bash_profile ~/.bash_profile

if [ -f ~/.bash_login ]
then
    cp ~/.bash_login ~/.bash_login.${DATE}
fi

echo "Now you must log out and back in again to pick up the new settings." >&2
