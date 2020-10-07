INSTALLAZIONE

# Da zero
1) $ conda create -n gavi python=3.7.9
2) $ conda activate gavi
3) $ conda install -c snap-stanford snap-stanford   # IMPORTANTE
4) $ conda install -c anaconda pyqt
	...
5) $ conda remove --name nome_virtual_env --all

6) conda list --explicit > spec-file.txt

# Da file spec solo con MAC-OSx
1) $ cd directory_progetto
2) $ conda create --name nome_virtual_env --file spec-file.txt
3) $ conda activate nome_virtual_env
3) $ python app.py