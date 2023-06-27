#Author- Melisa D Kaner
#Description- A helpful little script to automate contour generation for electronics users in the manufacturing workspace 

import adsk.core, adsk.fusion, adsk.cam, traceback, os



def run(context):
    global ui
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
        # template_name = "face.f3dhsm-template"
        template_name = "PCB CONTOUR SETH.f3dhsm-template"
        template_abs_path = os.path.join(folder, template_name)

        # Grab appropriate bodies
        # 1. Board (including cutouts?)
        # 2. Traces
        # Random test bdoy
        brep_body = ui.selectEntity('Select copper geometry to engrave', 'Bodies')
        
        selected_brep_body = adsk.fusion.BRepBody.cast(brep_body.entity)
        ui.messageBox(str(selected_brep_body.name))
        # selected_brep_body =cam_product.designRootOccurrence.bRepBodies.item(0)



        # Name the operation
        operation_name = "PCB Engrave"

        # Create setup
        # setup_name = "Test Setup" # Name the setup
        # setup = create_setup(cam_product=cam_product, brep_body=selected_brep_body, setup_name=setup_name)
        """
        for item in cam.setups:
            if setup.isActive:
                setup = item
        """
        create_new_operation(cam_product=cam_product, templateFilename=template_abs_path, operation_name=operation_name, bodyToMachine = selected_brep_body)

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

def create_new_operation(cam_product, templateFilename, operation_name, bodyToMachine):
        
    # List of all setups
    # setups:adsk.cam.Setups = cam_product.setups
    
    # Specify the full filename of the template.
    #templateFilename = 'E:\\face.f3dhsm-template'
    
    # Check if the template exists (from the path specified above). Show an error if it doesn't exist.
    if not os.path.exists(templateFilename):
        ui.messageBox("The template '" + templateFilename + "' does not exist")
        return

    # Go through each setup in the document
    #for setup in setups:
        # Add the template to each setup.
    
    # setup : adsk.cam.Setup = setups.item(setups.count -1)
    for item in cam_product.setups:
        if item.isActive:
            setup = item
    results = setup.createFromTemplate(templateFilename)

    """
    cadcontours2dParam: adsk.cam.CadContours2dParameterValue = input.parameters.itemByName('contours').value
    chains = cadcontours2dParam.getCurveSelections()
    # calculate and add a new silhouette curve to the geometry selection list
    chains.createNewSilhouetteSelection()
    cadcontours2dParam.applyCurveSelections(chains)
    """

    # Get the operation that was created. What's created will
    # vary depending on what's defined in the template so you
    # may need more logic to find the result you want.
    operation: adsk.cam.Operation = results.item(0)

    # Get operation parameter
    cadcontours2dParam: adsk.cam.CadContours2dParameterValue = operation.parameters.itemByName('contours').value
    chains = cadcontours2dParam.getCurveSelections()
    chains.item(0).inputGeometry = [bodyToMachine]
    cadcontours2dParam.applyCurveSelections(chains)


    operation. parameters.itemByName('bottomHeight_mode').expression = "'from surface bottom'"

    # Change the operation name
    operation.name = operation_name
    
    # Generate all toolpaths, skipping any that are already valid
    cam_product.generateAllToolpaths(True)