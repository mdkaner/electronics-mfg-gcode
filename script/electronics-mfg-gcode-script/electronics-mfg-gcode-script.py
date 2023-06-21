#Author- Melisa D Kaner
#Description- A helpful little script to automate contour generation for electronics users in the manufacturing workspace 

import adsk.core, adsk.fusion, adsk.cam, traceback, os



def run(context):
    ui = None
    try:
        
        # --------------- Setup ---------- #
        app = adsk.core.Application.get()
        ui  = app.userInterface
        # use existing document, load 2D Strategies model from the Fusion CAM Samples folder
        doc = app.activeDocument

        # switch to manufacturing space
        # camWS = ui.workspaces.itemById('CAMEnvironment') 
        # camWS.activate()

        # get the CAM product
        products = doc.products
        cam_product = adsk.cam.CAM.cast(products.itemByProductType("CAMProductType"))
        # --------------- Setup ---------- #
        
        # Get path of CAM template
        folder = os.path.dirname(os.path.abspath(__file__))
        template_name = "face.f3dhsm-template"
        template_abs_path = os.path.join(folder, template_name)

        # Grab appropriate bodies
        # 1. Board (including cutouts?)
        # 2. Traces
        # Random test bdoy
        brep_body_test =cam_product.designRootOccurrence.bRepBodies.item(0)

        # Name the setup
        setup_name = "Melisa Setup"

        # Name the operation
        operation_name = "Melisa operation"

        create_setup(cam_product=cam_product, brep_body=brep_body_test, setup_name=setup_name)
        create_new_operation(cam_product=cam_product, templateFilename=template_abs_path, operation_name=operation_name)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def create_setup(cam_product, brep_body, setup_name):
    # products = doc.products
    #cam = adsk.cam.CAM.cast(products.itemByProductType("CAMProductType"))
    setups = cam_product.setups
    setupInput = setups.createInput(adsk.cam.OperationTypes.MillingOperation)
    # create a list for the models to add to the setup Input
    models = [] 
    # part = cam_product.designRootOccurrence.bRepBodies.item(0)
    part = brep_body
    # add the part to the model list
    models.append(part) 
    # pass the model list to the setup input
    setupInput.models = models 
    # change some setup properties
    setupInput.name = setup_name
    setupInput.stockMode = adsk.cam.SetupStockModes.RelativeBoxStock
    # set offset mode
    setupInput.parameters.itemByName('job_stockOffsetMode').expression = "'simple'"
    # set offset stock side
    setupInput.parameters.itemByName('job_stockOffsetSides').expression = '0 mm'
    # set offset stock top
    setupInput.parameters.itemByName('job_stockOffsetTop').expression = '2 mm'
    # set setup origin
    setupInput.parameters.itemByName('wcs_origin_boxPoint').value.value = 'top 1'
    

    # create the setup
    setup = setups.add(setupInput) 

    return setup

def create_new_operation(cam_product, templateFilename, operation_name):
        # List of all setups
        setups = cam_product.setups
        
        # Specify the full filename of the template.
        #templateFilename = 'E:\\face.f3dhsm-template'
        
        # Check if the template exists (from the path specified above). Show an error if it doesn't exist.
        if not os.path.exists(templateFilename):
            ui.messageBox("The template '" + templateFilename + "' does not exist")
            return

        # Go through each setup in the document
        for setup in setups:
            # Add the template to each setup.
            results = setup.createFromTemplate(templateFilename)

            # Get the operation that was created. What's created will
            # vary depending on what's defined in the template so you
            # may need more logic to find the result you want.
            operation = results.item(0)

            # Change the operation name
            operation.name = operation_name
        
        # Generate all toolpaths, skipping any that are already valid
        cam_product.generateAllToolpaths(True)