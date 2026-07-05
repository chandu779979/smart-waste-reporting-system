// Google Maps JavaScript API Integration Script

let map;
let marker;
let geocoder;

function initMap() {
    geocoder = new google.maps.Geocoder();
    
    // Check if citizen complaint submission map is present
    const mapDiv = document.getElementById('map');
    if (mapDiv) {
        initCitizenMap(mapDiv);
    }
    
    // Check if admin/details view map is present
    const adminMapDiv = document.getElementById('map-admin');
    if (adminMapDiv) {
        initAdminMap(adminMapDiv);
    }
}

function initCitizenMap(mapDiv) {
    // Center of Andhra Pradesh by default
    const defaultLatLng = { lat: 15.9129, lng: 79.7400 };
    
    const latInput = document.getElementById('latitude');
    const lngInput = document.getElementById('longitude');
    const addressInput = document.getElementById('address');
    
    let initialLocation = defaultLatLng;
    let hasCoords = false;
    
    // Re-use already populated coords if present
    if (latInput && latInput.value && lngInput && lngInput.value) {
        const latVal = parseFloat(latInput.value);
        const lngVal = parseFloat(lngInput.value);
        if (!isNaN(latVal) && !isNaN(lngVal)) {
            initialLocation = { lat: latVal, lng: lngVal };
            hasCoords = true;
        }
    }
    
    map = new google.maps.Map(mapDiv, {
        center: initialLocation,
        zoom: hasCoords ? 15 : 8,
        styles: getDarkMapStyles()
    });
    
    if (hasCoords) {
        // Place active marker
        marker = new google.maps.Marker({
            position: initialLocation,
            map: map,
            draggable: true
        });
        setupMarkerListeners();
    } else {
        // Try getting user's browser location
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const pos = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude
                    };
                    map.setCenter(pos);
                    map.setZoom(14);
                },
                () => {
                    console.log("Geolocation service failed or permission denied.");
                }
            );
        }
    }
    
    // Map click placing a marker
    map.addListener('click', (event) => {
        placeMarker(event.latLng);
    });
    
    // Setup Autocomplete Search
    const searchInput = document.getElementById('map-search');
    if (searchInput) {
        const searchBox = new google.maps.places.SearchBox(searchInput);
        
        map.addListener('bounds_changed', () => {
            searchBox.setBounds(map.getBounds());
        });
        
        searchBox.addListener('places_changed', () => {
            const places = searchBox.getPlaces();
            if (places.length === 0) return;
            
            const place = places[0];
            if (!place.geometry || !place.geometry.location) return;
            
            map.setCenter(place.geometry.location);
            map.setZoom(16);
            placeMarker(place.geometry.location);
        });
        
        // Prevent enter key in search box from submitting the form
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
            }
        });
    }
    
    // Setup Get My Location button
    const btnGetLocation = document.getElementById('btn-get-location');
    if (btnGetLocation) {
        btnGetLocation.addEventListener('click', () => {
            getUserLocation(btnGetLocation);
        });
    }
}

function placeMarker(location) {
    if (marker) {
        marker.setPosition(location);
    } else {
        marker = new google.maps.Marker({
            position: location,
            map: map,
            draggable: true
        });
        setupMarkerListeners();
    }
    updateLocationInputs(location);
}

function setupMarkerListeners() {
    marker.addListener('dragend', () => {
        updateLocationInputs(marker.getPosition());
    });
}

function updateLocationInputs(latLng) {
    const lat = latLng.lat();
    const lng = latLng.lng();
    
    const latInput = document.getElementById('latitude');
    const lngInput = document.getElementById('longitude');
    const addressInput = document.getElementById('address');
    
    if (latInput) latInput.value = lat;
    if (lngInput) lngInput.value = lng;
    
    // Geocode coords to formatted address
    if (geocoder) {
        geocoder.geocode({ location: latLng }, (results, status) => {
            if (status === 'OK' && results[0]) {
                if (addressInput) {
                    addressInput.value = results[0].formatted_address;
                }
            } else {
                if (addressInput) {
                    addressInput.value = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
                }
            }
        });
    }
}

function initAdminMap(adminMapDiv) {
    const lat = parseFloat(adminMapDiv.dataset.lat);
    const lng = parseFloat(adminMapDiv.dataset.lng);
    const address = adminMapDiv.dataset.address || '';
    
    if (isNaN(lat) || isNaN(lng)) return;
    
    const location = { lat: lat, lng: lng };
    
    map = new google.maps.Map(adminMapDiv, {
        center: location,
        zoom: 15,
        styles: getDarkMapStyles()
    });
    
    marker = new google.maps.Marker({
        position: location,
        map: map,
        title: address
    });
    
    const infoWindow = new google.maps.InfoWindow({
        content: `<div style="color: #0f172a; font-family: 'Outfit', sans-serif; font-size: 13px; font-weight: 550; padding: 4px;"><strong>Location Address:</strong><br>${address}</div>`
    });
    
    marker.addListener('click', () => {
        infoWindow.open(map, marker);
    });
    
    // Display popover automatically
    infoWindow.open(map, marker);
}

// Google Maps Dark Aesthetic Scheme
function getDarkMapStyles() {
    return [
        { elementType: "geometry", stylers: [{ color: "#1e293b" }] },
        { elementType: "labels.text.stroke", stylers: [{ color: "#1e293b" }] },
        { elementType: "labels.text.fill", stylers: [{ color: "#94a3b8" }] },
        {
            featureType: "administrative.locality",
            elementType: "labels.text.fill",
            stylers: [{ color: "#f1f5f9" }]
        },
        {
            featureType: "poi",
            elementType: "labels.text.fill",
            stylers: [{ color: "#cbd5e1" }]
        },
        {
            featureType: "poi.park",
            elementType: "geometry",
            stylers: [{ color: "#0f172a" }]
        },
        {
            featureType: "poi.park",
            elementType: "labels.text.fill",
            stylers: [{ color: "#475569" }]
        },
        {
            featureType: "road",
            elementType: "geometry",
            stylers: [{ color: "#334155" }]
        },
        {
            featureType: "road",
            elementType: "geometry.stroke",
            stylers: [{ color: "#1e293b" }]
        },
        {
            featureType: "road",
            elementType: "labels.text.fill",
            stylers: [{ color: "#64748b" }]
        },
        {
            featureType: "road.highway",
            elementType: "geometry",
            stylers: [{ color: "#475569" }]
        },
        {
            featureType: "road.highway",
            elementType: "geometry.stroke",
            stylers: [{ color: "#1e293b" }]
        },
        {
            featureType: "road.highway",
            elementType: "labels.text.fill",
            stylers: [{ color: "#e2e8f0" }]
        },
        {
            featureType: "transit",
            elementType: "geometry",
            stylers: [{ color: "#1e293b" }]
        },
        {
            featureType: "transit.station",
            elementType: "labels.text.fill",
            stylers: [{ color: "#f1f5f9" }]
        },
        {
            featureType: "water",
            elementType: "geometry",
            stylers: [{ color: "#0f172a" }]
        },
        {
            featureType: "water",
            elementType: "labels.text.fill",
            stylers: [{ color: "#475569" }]
        },
        {
            featureType: "water",
            elementType: "labels.text.stroke",
            stylers: [{ color: "#0f172a" }]
        }
    ];
}

// Geolocation fetcher function for citizen form
function getUserLocation(button) {
    const originalHTML = button.innerHTML;
    button.disabled = true;
    button.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Fetching location...`;
    
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                
                // Directly populate coordinates inputs
                const latInput = document.getElementById('latitude');
                const lngInput = document.getElementById('longitude');
                const addressInput = document.getElementById('address');
                
                if (latInput) latInput.value = lat;
                if (lngInput) lngInput.value = lng;
                
                // If Google Maps is loaded and authorized, move marker & center map
                if (typeof map !== 'undefined' && map && typeof google !== 'undefined' && google.maps && geocoder) {
                    const latLng = new google.maps.LatLng(lat, lng);
                    placeMarker(latLng);
                    map.setCenter(latLng);
                    map.setZoom(16);
                    
                    button.disabled = false;
                    button.innerHTML = originalHTML;
                } else {
                    // Fallback when Google Maps auth failed
                    if (addressInput && !addressInput.value) {
                        addressInput.value = "My Current Location";
                    }
                    showLocationError(button, originalHTML, "Coordinates fetched successfully. Since Google Maps is offline, please enter your address manually.");
                }
            },
            (error) => {
                let msg = "Could not fetch your location automatically. Please manually type the coordinates or click on the map.";
                if (error.code === error.PERMISSION_DENIED) {
                    msg = "Location permission denied. Please allow location access or manually select a location on the map.";
                }
                showLocationError(button, originalHTML, msg);
            },
            { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
        );
    } else {
        showLocationError(button, originalHTML, "Your browser does not support Geolocation. Please enter coordinates manually.");
    }
}

function showLocationError(button, originalHTML, message) {
    button.disabled = false;
    button.innerHTML = originalHTML;
    
    // Display error message near the map in a temporary container or alert
    let errDiv = document.getElementById('location-error-alert');
    if (!errDiv) {
        errDiv = document.createElement('div');
        errDiv.id = 'location-error-alert';
        errDiv.className = 'alert alert-warning card-glass mt-2 d-flex align-items-center';
        errDiv.innerHTML = `
            <i class="fa-solid fa-circle-exclamation me-2 text-warning"></i>
            <div style="font-size: 0.85rem;">${message}</div>
            <button type="button" class="btn-close btn-close-white ms-auto" style="font-size: 0.75rem;" onclick="this.parentElement.remove()"></button>
        `;
        button.parentElement.parentElement.appendChild(errDiv);
    } else {
        errDiv.querySelector('div').innerText = message;
    }
}

// Google Maps authentication failure callback - automatically falls back to Leaflet + OpenStreetMap
window.gm_authFailure = function() {
    console.warn("Google Maps auth failure detected. Initializing Leaflet fallback...");
    triggerLeafletFallback();
};

function triggerLeafletFallback() {
    const mapDiv = document.getElementById('map');
    if (mapDiv) {
        // Default coordinates: center of India (e.g. 20.5937, 78.9629) or Andhra Pradesh (15.9129, 79.7400)
        const latInput = document.getElementById('latitude');
        const lngInput = document.getElementById('longitude');
        let lat = 15.9129;
        let lng = 79.7400;
        
        if (latInput && latInput.value && lngInput && lngInput.value) {
            const pLat = parseFloat(latInput.value);
            const pLng = parseFloat(lngInput.value);
            if (!isNaN(pLat) && !isNaN(pLng)) {
                lat = pLat;
                lng = pLng;
            }
        }
        loadLeafletFallback('map', lat, lng, true);
    }
    const adminMapDiv = document.getElementById('map-admin');
    if (adminMapDiv) {
        const lat = parseFloat(adminMapDiv.dataset.lat) || 15.9129;
        const lng = parseFloat(adminMapDiv.dataset.lng) || 79.7400;
        loadLeafletFallback('map-admin', lat, lng, false);
    }
}

// Function to load Leaflet dynamically from CDN
function loadLeafletFallback(mapDivId, lat, lng, isSelector) {
    // 1. Add Leaflet CSS
    if (!document.getElementById('leaflet-css')) {
        const link = document.createElement('link');
        link.id = 'leaflet-css';
        link.rel = 'stylesheet';
        link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
        document.head.appendChild(link);
    }
    
    // 2. Add Leaflet JS
    if (typeof L === 'undefined') {
        const script = document.createElement('script');
        script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
        script.onload = () => {
            initializeLeaflet(mapDivId, lat, lng, isSelector);
        };
        script.onerror = () => {
            console.error("Failed to load Leaflet JS fallback.");
        };
        document.head.appendChild(script);
    } else {
        initializeLeaflet(mapDivId, lat, lng, isSelector);
    }
}

function initializeLeaflet(mapDivId, lat, lng, isSelector) {
    const container = document.getElementById(mapDivId);
    if (!container) return;
    
    // Clear Google Maps error boxes or alerts
    container.innerHTML = '';
    
    // Initialize Leaflet map instance
    const lMap = L.map(mapDivId).setView([lat, lng], isSelector ? 11 : 14);
    
    // Add OpenStreetMap tile layers
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(lMap);
    
    // Add custom draggable marker
    const markerOptions = { draggable: isSelector };
    const lMarker = L.marker([lat, lng], markerOptions).addTo(lMap);
    
    if (isSelector) {
        // Drag listener
        lMarker.on('dragend', function() {
            const pos = lMarker.getLatLng();
            updateLeafletCoords(pos.lat, pos.lng);
        });
        
        // Map click listener
        lMap.on('click', function(e) {
            const pos = e.latlng;
            lMarker.setLatLng(pos);
            updateLeafletCoords(pos.lat, pos.lng);
        });
        
        // Wire up "Get My Location" button for Leaflet
        const btnGetLocation = document.getElementById('btn-get-location');
        if (btnGetLocation) {
            // Replace the old Google-reliant listener
            const newBtn = btnGetLocation.cloneNode(true);
            btnGetLocation.parentNode.replaceChild(newBtn, btnGetLocation);
            
            newBtn.addEventListener('click', () => {
                const originalHTML = newBtn.innerHTML;
                newBtn.disabled = true;
                newBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Fetching location...`;
                
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(
                        (position) => {
                            const uLat = position.coords.latitude;
                            const uLng = position.coords.longitude;
                            
                            lMarker.setLatLng([uLat, uLng]);
                            lMap.setView([uLat, uLng], 15);
                            updateLeafletCoords(uLat, uLng);
                            
                            newBtn.disabled = false;
                            newBtn.innerHTML = originalHTML;
                        },
                        (error) => {
                            newBtn.disabled = false;
                            newBtn.innerHTML = originalHTML;
                            alert("Could not fetch location automatically. Please click on the map manually.");
                        }
                    );
                } else {
                    newBtn.disabled = false;
                    newBtn.innerHTML = originalHTML;
                    alert("Geolocation is not supported by your browser.");
                }
            });
        }
        
        // Wire up OSM Location Autocomplete search box
        const searchInput = document.getElementById('map-search');
        if (searchInput) {
            // Replace old listeners
            const newSearch = searchInput.cloneNode(true);
            searchInput.parentNode.replaceChild(newSearch, searchInput);
            
            newSearch.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    searchLocationLeaflet(newSearch.value, lMap, lMarker);
                }
            });
        }
    } else {
        // Admin detail map popup
        const address = container.dataset.address || 'Report Location';
        lMarker.bindPopup(`<strong>Location:</strong><br>${address}`).openPopup();
    }
}

function searchLocationLeaflet(query, lMap, lMarker) {
    if (!query) return;
    const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`;
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data && data.length > 0) {
                const item = data[0];
                const lat = parseFloat(item.lat);
                const lng = parseFloat(item.lon);
                
                lMap.setView([lat, lng], 14);
                lMarker.setLatLng([lat, lng]);
                updateLeafletCoords(lat, lng);
            } else {
                alert("Location not found. Please try search landmarks or enter manually.");
            }
        })
        .catch(err => console.error("Search failed:", err));
}

function updateLeafletCoords(lat, lng) {
    const latInput = document.getElementById('latitude');
    const lngInput = document.getElementById('longitude');
    const addressInput = document.getElementById('address');
    
    if (latInput) latInput.value = lat;
    if (lngInput) lngInput.value = lng;
    
    // Free OpenStreetMap reverse geocoding
    const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`;
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data && data.display_name) {
                if (addressInput) addressInput.value = data.display_name;
            } else {
                if (addressInput) addressInput.value = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
            }
        })
        .catch(() => {
            if (addressInput) addressInput.value = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
        });
}
