Imports KnowledgewareTypeLib
Imports MECMOD
Imports Newtonsoft.Json
Imports System.IO
Imports ProductStructureTypeLib


Public Class Form1


    Public Shared CATIA As INFITF.Application = GetObject(vbNullString, "Catia.Application")
    Public Shared Objects2select = CATIA.ActiveDocument.Selection
    Public Shared documents1 = CATIA.Documents


    Public Shared Function modify_parameters(documents1, products1, Part_Name, Parameter_name, Parameter_Value)
        Debug.Print(Parameter_name & " modified  to " & Parameter_Value)
        Dim I_Part = documents1.Item(products1.Item(Part_Name).PartNumber & ".CATPart")
        Dim I_Part_Part = I_Part.Part
        Dim Parameter2 = I_Part_Part.Parameters
        Dim position1 = Parameter2.item(Parameter_name)
        position1.value = Parameter_Value
        'Part.Update()
    End Function

    ' Define a class to hold the brick data
    Public Class Brick
        Public Property brick As Integer()
        Public Property position As Integer()
    End Class


    Private Sub Button1_Click(sender As Object, e As EventArgs) Handles Button1.Click
        Dim partDocument1 As ProductDocument = documents1.Item("Product_init.CATProduct")
        Dim product1 = partDocument1.Product
        Dim products1 = product1.Products
        Dim parameters1 = product1.Parameters
        Dim Relations1 = product1.Relations

        'Dim json As String = File.ReadAllText("\\ad.liu.se\home\matga917\Documents\Cad nibbas\TMKT57\JSON2LEGO\latest_bricks_placed.json")
        Dim json As String = File.ReadAllText("\\ad.liu.se\home\matga917\Documents\Cad nibbas\TMKT57\JSON2LEGO\pyramid_1x1voxel_array.json")
        Dim bricks As List(Of Brick) = JsonConvert.DeserializeObject(Of List(Of Brick))(json)

        ' Reset ProgressBar color to default (usually Green)
        ProgressBar1.ForeColor = Color.Green

        ' Set the maximum value of the ProgressBar to the number of bricks
        ProgressBar1.Value = 0
        ProgressBar1.Maximum = bricks.Count

        ' Set the Step property of the ProgressBar to the number of bricks
        ProgressBar1.Step = bricks.Count

        ' Clear the Label's text
        Label1.Text = ""

        ' Store the start time
        Dim startTime As DateTime = DateTime.Now

        For Each brick In bricks
            ' Instance the brick
            Dim New_Part = products1.AddNewComponent("Part", "")
            New_Part.Name = $"Instance_size{brick.brick(0)}x{brick.brick(1)}x{brick.brick(2)}_pos{brick.position(0)}x{brick.position(1)}x{brick.position(2)}"

            Dim NewPartNumber = New_Part.PartNumber
            Dim PasteInPart As PartDocument = documents1.Item(NewPartNumber & ".CATPart")
            Dim Parameter2 As Parameters = PasteInPart.Part.Parameters
            Objects2select.clear()
            Dim Paste_In = PasteInPart.Part.HybridBodies
            Objects2select.Add(Paste_In)
            Objects2select.PasteSpecial("CATPrtResult")


            Dim I_Part As PartDocument = documents1.Item(New_Part.PartNumber & ".CATPart")
            Dim I_Part_Part = I_Part.Part
            '------- Set the current part as destination of the instantiation (2)
            Dim factory = I_Part_Part.GetCustomerFactory("InstanceFactory")
            '------- Locate the Power Copy and Part in which the template is located (3)
            factory.BeginInstanceFactory("PowerCopy_brick", "\\ad.liu.se\home\matga917\Documents\Cad nibbas\TMKT57\JSON2LEGO\Lego1_Approach2.CATPart") '------- Need to be modified
            '------- Start the Instantiation Process (4)
            factory.BeginInstantiate
            '------- Set the Constraints for the template (5)
            Dim Item_to_set1 = I_Part_Part.FindObjectByName("xy plane") '------- Need to be modified
            factory.PutInputData("xy plane", Item_to_set1) '------- Need to be modified
            '------- Create the instance (6)
            Dim Instance = factory.Instantiate
            '------- End the Instantiation Process (7)
            factory.EndInstantiate
            '------- Release the template model (8)
            factory.EndInstanceFactory
            '------- Update the current part (9)
            I_Part_Part.Update()

            ' Set the brick position
            modify_parameters(documents1, products1, New_Part.Name, "pos_X", brick.position(2) * 7.8)
            modify_parameters(documents1, products1, New_Part.Name, "pos_Y", brick.position(1) * 7.8)
            modify_parameters(documents1, products1, New_Part.Name, "pos_Z", brick.position(0) * 9.6)

            ' Set the brick dimensions
            'modify_parameters(documents1, products1, New_Part.Name, "Nr_Of_Cylinders_in_X", brick.brick(2))
            'modify_parameters(documents1, products1, New_Part.Name, "Nr_Of_Cylinders_in_Y", brick.brick(1))

            I_Part_Part.Update()

            ' Update the ProgressBar
            ProgressBar1.Value += 1

            Calculate the progress percentage
            Dim progressPercentage As Integer = CInt((ProgressBar1.Value / ProgressBar1.Maximum) * 100)

            ' Calculate elapsed and remaining time
            Dim elapsedTime As TimeSpan = DateTime.Now - startTime
            Dim remainingTime As TimeSpan = TimeSpan.FromTicks((elapsedTime.Ticks / ProgressBar1.Value) * (ProgressBar1.Maximum - ProgressBar1.Value))

            ' Update the Label's text with progress and estimated time remaining
            Label1.Text = $"{progressPercentage}% - Estimated time remaining: {remainingTime.ToString(@"hh\:mm\:ss")}"
        Next


    End Sub

    Private Sub Button2_Click(sender As Object, e As EventArgs) Handles Button2.Click
        Dim partDocument1 As ProductDocument = documents1.Item("Product_init.CATProduct")
        Dim product1 = partDocument1.Product
        Dim products1 = product1.Products

        ' Set the maximum value of the ProgressBar to the number of products
        ProgressBar1.Maximum = products1.Count
        ProgressBar1.Value = 0
        ProgressBar1.ForeColor = Color.Red  ' Change ProgressBar color to Red

        ' Clear the Label's text
        Label1.Text = ""

        ' Store the start time
        Dim startTime As DateTime = DateTime.Now

        For i = products1.Count To 1 Step -1
            Dim product = products1.Item(i)
            If product.Name <> "References" Then
                products1.Remove(i)

                ' Update the ProgressBar
                ProgressBar1.Value += 1

                'Calculate the progress percentage
                Dim progressPercentage As Integer = CInt((ProgressBar1.Value / ProgressBar1.Maximum) * 100)

                ' Calculate elapsed and remaining time
                Dim elapsedTime As TimeSpan = DateTime.Now - startTime
                Dim remainingTime As TimeSpan = TimeSpan.FromTicks((elapsedTime.Ticks / ProgressBar1.Value) * (ProgressBar1.Maximum - ProgressBar1.Value))

                ' Update the Label's text with progress and estimated time remaining
                Label1.Text = $"{progressPercentage}% - Estimated time remaining: {remainingTime.ToString(@"hh\:mm\:ss")}"
            End If
        Next

        ' Reset ProgressBar and Label
        ProgressBar1.Value = ProgressBar1.Maximum
        Label1.Text = ""


        product1.Update()


    End Sub

End Class