
/**
 *  Created By: Nicholas Evans
 *  Project Start Date: May 19th, 2020
 *  Client Version 1.2
 */

document.addEventListener("DOMContentLoaded", function(event) {


    function keepServerAlive() {
        axios.get('/keepAlive', '')
        .then(function (response){
            console.log(response)
    
        }).catch(function(error){
            console.log(error)
            console.log(error.response)
        })
    }
    
    //Send keep alive signal every 5 seconds
    keepServerAlive()
    intervalID = setInterval(keepServerAlive, 5000)

    var app = new Vue({
        el: "#app", 
        data: {
            total_tips: 0,          //Total tips, inputed from the form
            employee_data: [],      //List of lists/dictionaries for each employee  
            stats: [' ',' ',' ',' ',' ', ' '],  //List of stats
            tip_error: '',          //Display error when adding total tips
            file_error: '',         //Display error if no file is given
            add_error: '',          //Display error when adding invalid employee
            isAsc: true,            //Controls direction of sort in table
            settings: [],           //Dictionary with all user settings
            warning_msg: '',        //Display warning about making sure all employees are added
                                    //and ones that shouldn't be there are removed
        }, //End of data

        methods:{
            sendFile: function () {
                var app = this

                app.tip_error = ''
                app.file_error = ''
                app.add_error = ''

                app.total_tips = document.getElementById('total-tips').value

                //Validate and round total_tips input
                if(!isValidNumber(app.total_tips)){
                    console.log('Invalid number: '+app.total_tips)
                    app.tip_error = 'Total tips can only be a number, ex: 10 or 10.53.'
                    return
                }
                app.total_tips = (+app.total_tips).toFixed(2)
                
                app.tip_error = '';
                let axiosConfig = {
                    headers: {
                            "Content-Type": "multipart/form-data",
                            "cache-control": "no-cache",
                            "processData": false,
                            "contentType": false,
                            "mimeType": "multipart/form-data",
                    }
                };
                
                var file = document.getElementById('file')
                if(file.files.length == 0){
                    app.file_error = 'Please include a file.'
                    return
                }

                keepServerAlive()
                
                var formData = new FormData()
                
                const blob = new Blob([file.files[0]], {type: 'application/pdf'})
                formData.append("file", blob, 'work_report.pdf')
                
                axios.post('/generate', formData, axiosConfig)
                .then(function (response){
                    var temp_employee_data = response.data.response.employees
                    
                    app.employee_data = []
                    for(var e in temp_employee_data){
                        app.employee_data.push(
                            {
                                id:temp_employee_data[e][0], name:temp_employee_data[e][1], 
                                hours:temp_employee_data[e][2], percent:temp_employee_data[e][3], 
                                amount:temp_employee_data[e][4]
                            }
                        )
                    }

                    app.isAsc = false
                    app.sortTable(0)
                    
                    app.setTipsAndPercent()
                    app.setStats()

                    app.warning_msg =   "Make sure all employees are added to the list, and add any that are missing. "+
                                        "Also make sure that any employees that shouldn't be on the list are removed. "

                })  //End of then
                .catch(function(error){
                    console.log(error)
                    console.log(error.response)
                })  //End of catch
                
            },  //End of sendFile

            resetInputs: function() {
                var app = this;
                
                app.total_tips = 0
                document.getElementById('total-tips').value = ''
                
                document.getElementById('file').value = ''
                
                app.tip_error = ''
                document.getElementById('tip-error').value = ''
                
                app.file_error = ''
                document.getElementById('file-error').value = ''

                app.add_error = ''
                document.getElementById('add-error').value = ''

                app.warning_msg = ''
                document.getElementById('warning-msg-1').value = ''
                document.getElementById('warning-msg-2').value = ''

                app.stats = [' ',' ',' ',' ',' ']
            },  //End of resetInputs
            isEmpty: function() {
                var app = this
                if(app.employee_data.length == 0){
                    return true
                }
                return false
            },  //End of isEmpty
            
            sortTable: function(col) {
                var app = this
                app.isAsc = !app.isAsc
                //Sort by Employee ID
                if(col == 0){
                    if(app.isAsc){
                        app.employee_data.sort((a,b) => (a.id > b.id) ? 1 : -1)
                    }else{
                        app.employee_data.sort((a,b) => (a.id < b.id) ? 1 : -1)
                    }
                }
                //Sort by Employee Name
                else if(col == 1){
                    if(app.isAsc){
                        app.employee_data.sort((a,b) => (a.name > b.name) ? 1 : -1)
                    }else{
                        app.employee_data.sort((a,b) => (a.name < b.name) ? 1 : -1)
                    }
                }
                //Sort by Hours Worked, Tip Percent and Tip Amount, since all will sort the same
                else if(col == 2){
                    if(app.isAsc){
                        app.employee_data.sort((a,b) => (a.hours > b.hours) ? 1 : -1)
                    }else{
                        app.employee_data.sort((a,b) => (a.hours < b.hours) ? 1 : -1)
                    }
                }else{
                    console.log("You shouldn't be here")
                }
            },  //End of sortTable

            setStats: function() {
                var app = this

                totalHours = app.getTotalHours()
                var actual = app.getAdjustedTotalTipAmount()
                app.stats[0] = app.employee_data.length + " Employees"
                app.stats[1] = "$"+app.calculateDollarsAnHour(actual, totalHours).toFixed(2) + "/Hour Each"
                app.stats[2] = totalHours + " Total Hours"
                app.stats[3] = "Tip Percent: " + Math.ceil(app.getTipPercent()) + "%"
                
                
                var tipOffset = Math.abs(app.total_tips - actual).toFixed(2)
                if(actual > app.total_tips) {
                    app.stats[4] = format_currency(tipOffset)+ " over ("+format_currency(actual)+")"
                }else if(actual < app.total_tips) {
                    app.stats[4] = format_currency(tipOffset)+ " under ("+format_currency(actual)+")"
                }else {
                    app.stats[4] = format_currency(actual) + " even"
                }
            },  //End of setStats

            calculateDollarsAnHour: function(tips, hours) {
                var app = this
                return tips/hours

            },  //End of calculateDollarsAnHour

            addEmployee: function() {
                var app = this

                var id = document.getElementById("newID").value
                var name = document.getElementById("newName").value
                var hours = document.getElementById("newHours").value
                
                if(id == '' || name == '' || hours == ''){
                    app.add_error = 'No field can be left empty.'
                    return
                }

                if(!isValidNumber(hours)){
                    app.add_error = 'Hours needs to be a number, ex: 10 or 10.53.'
                    return
                }

                for(var e in app.employee_data){
                    if(app.employee_data[e].id == id){
                        app.add_error = 'Someone already has that employee ID.'
                        return
                    }
                }
                app.add_error = ''
                app.employee_data.push({id:id, name:name, hours:+hours, percent:'0%', amount:'$0'})
                
                //Recalculate tips and stats
                app.setTipsAndPercent()
                app.setStats()

                //Clear  input fields
                document.getElementById("newID").value = ''
                document.getElementById("newName").value = ''
                document.getElementById("newHours").value = ''

            },  //End of addEmployee

            removeEmployee: function(id) {
                var app = this

                var i = 0
                for(var e in app.employee_data){
                    if(app.employee_data[e].id == id){
                        app.employee_data.splice(i,1)
                        break
                    }
                    i++
                }

                //Recalculate tips and stats
                app.setTipsAndPercent()
                app.setStats()

            },  //End of removeEmployee

            setTipsAndPercent: function() {
                var app = this

                var totalHours = app.getTotalHours()

                for(var e in app.employee_data){
                    var emp = app.employee_data[e]
                    emp.percent = ((emp.hours/totalHours) * 100).toFixed(2) + "%"
                    emp.amount = ((emp.hours/totalHours) * app.total_tips).toFixed(2)
                    if(emp.amount%1 >= 0.20) {
                        emp.amount = "$"+Math.ceil(emp.amount)
                    }else{
                        emp.amount = "$"+Math.floor(emp.amount)
                    }
                }
            },  //End of setTipsAndPercent

            getTotalHours: function() {
                var app = this
                var totalHours = 0
                for(var e in app.employee_data){
                    totalHours += app.employee_data[e].hours
                }
                return totalHours.toFixed(2)
            },  //End of getTotalHours

            getAdjustedTotalTipAmount: function() {
                var app = this
                var adjusted = 0
                for(var e in app.employee_data){
                    adjusted += +((""+app.employee_data[e].amount).slice(1))

                }
                return adjusted.toFixed(2)
            },  //End of getAdjustedTotalTipAmount

            getTipPercent: function() {
                var app = this

                var tipPercent = 0
                for(var e in app.employee_data){
                    tipPercent += parseFloat(app.employee_data[e].percent)
                }

                return tipPercent.toFixed(2)
            },   //End of getTipPercent

            openSettings: function(){
                clearInterval(intervalID)
                window.location.href = "http://localhost:5000/settings"
            },  //End of openSettings

        }   //End of methods
    }); //End of app
});

function isValidNumber(s){
    return !isNaN(s - parseFloat(s));
}

function format_currency(number){
    return "$" + parseFloat(number).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')
}