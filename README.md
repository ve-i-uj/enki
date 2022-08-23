# Enki (Godot network plugin for connecting with KBEngine)

## Development

Install pyenv

```
PROJECT_DIR=<YOUR_PROJ_DIR>
git clone git@github.com:ve-i-uj/enki.git $PROJECT_DIR
cd $PROJECT_DIR
bash scripts/pyvenv/make.sh
```

## Structure

* enki - library for the application and the code generator. It contains the client to the kbe server, external interfaces, base classes and generated code.
* ninmah - a code generator
* damkina - an application
