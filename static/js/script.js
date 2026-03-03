let map;
let directionsService;
let directionsRenderer;
let locationCount = 0;

function initMap() {
  map = new google.maps.Map(document.getElementById("map"), {
    zoom: 6,
    center: { lat: 11.0168, lng: 76.9558 }
  });

  directionsService = new google.maps.DirectionsService();
  directionsRenderer = new google.maps.DirectionsRenderer();
  directionsRenderer.setMap(map);

  addLocation();
  addLocation();
}

function addLocation() {
  locationCount++;

  const div = document.createElement("div");
  div.innerHTML = `
    <input type="text" placeholder="Enter DC Code (JP4)" id="dc${locationCount}">
  `;

  document.getElementById("inputs").appendChild(div);
}

function calculateRoute() {
  const locations = [];

  for (let i = 1; i <= locationCount; i++) {
    const code = document.getElementById(`dc${i}`).value.trim();
    if (code !== "") {
      locations.push(code);
    }
  }

  if (locations.length < 2) {
    alert("Minimum 2 DC codes required!");
    return;
  }

  fetch("/calculate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ locations: locations })
  })
  .then(res => res.json())
  .then(data => {

    if (data.error) {
      alert(data.error);
      return;
    }

    document.getElementById("result").innerHTML =
      `Total Distance: ${data.distance_km} km | Total Time: ${data.duration_hr} hrs`;

    const waypoints = data.coordinates.slice(1, data.coordinates.length - 1).map(loc => ({
      location: loc,
      stopover: true
    }));

    directionsService.route({
      origin: data.coordinates[0],
      destination: data.coordinates[data.coordinates.length - 1],
      waypoints: waypoints,
      travelMode: 'DRIVING'
    }, function(response, status) {
      if (status === 'OK') {
        directionsRenderer.setDirections(response);
      }
    });

  });
}