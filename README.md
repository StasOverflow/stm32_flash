# STM32 FLASHER
-----

##### Instructions are valid only for Win10 platform 

To install the app:

- Activate virtualenv

        $ python -m venv env
        
        -For linux:   
            $ source .env/bin/activate
        
        -For windows:
            $ .\env\Scripts\activate
            
        Note: deactivation of virtualenv can be perfromed by:
            $ decativate 
            

- Install requirements

        $ pip install -r requirements.txt
        
        - You might also need download and install pywin32 from:
            https://sourceforge.net/projects/pywin32/files/
    
- Install wxPython for your platform
        
        Win10:
            $ pip install -U wxPython

- Run installation script
        
        $ pyinstaller app.spec
        
        - To create .spec file run: 
            $ pyi-makespec app.py
            
        
- Proceed to dist directory and run `.exe` file