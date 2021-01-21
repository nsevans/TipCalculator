/**
 *  Created By: Nicholas Evans
 *  Project Start Date: May 19th, 2020
 *  Client Version 1.2
 */

document.addEventListener("DOMContentLoaded", function(event){
    
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
    intervalID =setInterval(keepServerAlive, 5000)
    
    var app = new Vue({
        el: "#app",
        data: {
            employee_names: [],    //List of all employees that can get tips
            isAsc: true,           //Control direction of sort in table
            add_error: '',         //Error if added employee already exists (Names match exactly (Not case sensitive))
        }, //End of data

        created: function(){
            keepServerAlive()
            this.getSettings();
        }, //End of created

        methods:{
            getSettings: function() {
                var app = this
                app.add_error = ''

                let axiosConfig = {
                    headers: {
                    'Content-Type': 'application/json;charset=UTF-8',
                    "Access-Control-Allow-Origin": "*",
                    }
                };

                axios.get('/settings_get', axiosConfig)
                .then(function(response){
                    settings = response.data.settings
                    console.log(settings)
                    app.employee_names = settings
                    
                    

                }) //End of then
                .catch(function(error){
                    console.log(error)
                }); //End of catch 
            },   //End of getSettings

            addEmployee: function() {
                var app = this

                var name = document.getElementById("newName").value

                for (var n in app.employee_names){
                    if(app.employee_names[n] == name){
                        app.add_error = "An employee already exists with that name"
                        return
                    }
                }

                app.add_error
                app.employee_names.push(name)

                document.getElementById("newName").value = ""

                app.sortTable()

            },  //End of addEmployee

            removeEmployee: function(name) {
                var app = this
                var i = 0
                for(var e in app.employee_names){
                    if(app.employee_names[e] == name){
                        app.employee_names.splice(i,1)
                        break
                    }
                    i++
                }
            },  //End of removeEmployee

            sortTable: function() {
                var app = this
                app.isAsc = !app.isAsc

                if(app.isAsc){
                    app.employee_names.sort((a,b) => (a > b) ? 1 : -1)
                }else{
                    app.employee_names.sort((a,b) => (a < b) ? 1 : -1)
                }
            },  //End of sortTable
            
            saveSettings: function() {
                var app = this
                console.log("Saving settings...")

                let axiosConfig = {
                    headers: {
                        'Content-Type': 'application/json;charset=UTF-8',
                        "Access-Control-Allow-Origin": "*"
                    }
                };
                axios.post('/settings_update', app.employee_names, axiosConfig)
                .then(function (response){
                    console.log(response)
                    app.backToMain()

                }) //End of then
                .catch(function(error){
                    console.log(error)
                    console.log(error.response)
                }) //End of cathc

            },  //End of saveSettings

            backToMain: function() {
                clearInterval(intervalID)
                window.location.href = "http://localhost:5000/"
            },  //End of backToMain
        }   // End of methods
    }); //End of app
});