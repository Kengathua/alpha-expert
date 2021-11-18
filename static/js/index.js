// function myFunction() {
//   console.log("Found it")
// }

function myfunction() {   
    alert("how are you");  
         }

function slider(){
    console.log("Slider selected")
}

function getApi(){
    url='http://127.0.0.1:8000/analysis/Results/'
    fetch(url);
    .then(response => response.json());
    .then(data => console.log(data));
    }