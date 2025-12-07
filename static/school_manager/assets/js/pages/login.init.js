/**
 * Script pour gérer les notifications SweetAlert2 et la connexion AJAX sur la page de login
 */

// Fonction pour obtenir le token CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Fonction pour afficher les messages Django avec SweetAlert2
function displayDjangoMessages() {
    const messagesContainer = document.getElementById('django-messages');
    if (messagesContainer) {
        const messageElements = messagesContainer.querySelectorAll('div[data-tags]');
        
        messageElements.forEach(function(element) {
            const tags = element.getAttribute('data-tags');
            const message = element.getAttribute('data-message');
            
            // Ignorer les messages d'erreur génériques qui ne sont pas pertinents
            // lors d'un accès GET (première visite de la page)
            if (tags === 'error' || tags.includes('error')) {
                const genericMessages = [
                    'veuillez corriger les erreurs ci-dessous',
                    'please correct the errors below',
                    'corrigez les erreurs ci-dessous'
                ];
                const messageLower = message.toLowerCase();
                if (genericMessages.some(genericMsg => messageLower.includes(genericMsg))) {
                    // Ne pas afficher ce message générique
                    return;
                }
            }
            
            // Déterminer le type et l'icône selon les tags Django
            let icon = 'info';
            let title = 'Information';
            
            if (tags === 'success' || tags.includes('success')) {
                icon = 'success';
                title = 'Succès';
            } else if (tags === 'error' || tags.includes('error')) {
                icon = 'error';
                title = 'Erreur';
            } else if (tags === 'warning' || tags.includes('warning')) {
                icon = 'warning';
                title = 'Attention';
            } else if (tags === 'info' || tags.includes('info')) {
                icon = 'info';
                title = 'Information';
            }
            
            // Afficher la notification SweetAlert2
            Swal.fire({
                icon: icon,
                title: title,
                text: message,
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 3000,
                timerProgressBar: true,
                didOpen: (toast) => {
                    toast.addEventListener('mouseenter', Swal.stopTimer);
                    toast.addEventListener('mouseleave', Swal.resumeTimer);
                }
            });
        });
    }
}

// Gérer la soumission du formulaire avec AJAX
document.addEventListener('DOMContentLoaded', function() {
    // Afficher les messages Django existants
    displayDjangoMessages();
    
    // Intercepter la soumission du formulaire
    const loginForm = document.querySelector('form[method="post"]');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Empêcher la soumission normale
            
            // Récupérer les valeurs du formulaire
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;
            const rememberMe = document.getElementById('remember_me').checked;
            
            // Validation côté client
            if (!username || !password) {
                Swal.fire({
                    icon: 'error',
                    title: 'Erreur',
                    text: 'Veuillez remplir tous les champs',
                    toast: true,
                    position: 'top-end',
                    showConfirmButton: false,
                    timer: 3000
                });
                return;
            }
            
            // Afficher un loader
            const submitButton = loginForm.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Connexion...';
            
            // Récupérer le token CSRF
            const csrftoken = getCookie('csrftoken');
            
            // Préparer les données
            const formData = {
                username: username,
                password: password,
                remember_me: rememberMe
            };
            
            // Envoyer la requête AJAX
            fetch('/profiles/login/ajax/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(formData)
            })
            .then(response => {
                return response.json().then(data => {
                    return { status: response.status, data: data };
                });
            })
            .then(result => {
                // Restaurer le bouton
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
                
                if (result.status === 200 && result.data.status === 'success') {
                    // Succès - Afficher un message et rediriger
                    const welcomeName = result.data.full_name || result.data.username || '';
                    Swal.fire({
                        icon: 'success',
                        title: 'Connexion réussie',
                        text: 'Bienvenue ' + welcomeName + ' !',
                        toast: true,
                        position: 'top-end',
                        showConfirmButton: false,
                        timer: 2000,
                        timerProgressBar: true
                    }).then(() => {
                        // Rediriger vers le dashboard
                        window.location.href = '/profiles/dashboard/';
                    });
                } else {
                    // Erreur - Afficher le message d'erreur
                    const errorMessage = result.data.message || 'Une erreur est survenue lors de la connexion';
                    Swal.fire({
                        icon: 'error',
                        title: 'Erreur de connexion',
                        text: errorMessage,
                        toast: true,
                        position: 'top-end',
                        showConfirmButton: false,
                        timer: 4000,
                        timerProgressBar: true
                    });
                }
            })
            .catch(error => {
                // Erreur réseau ou autre
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
                
                Swal.fire({
                    icon: 'error',
                    title: 'Erreur',
                    text: 'Une erreur réseau est survenue. Veuillez réessayer.',
                    toast: true,
                    position: 'top-end',
                    showConfirmButton: false,
                    timer: 4000
                });
                console.error('Erreur:', error);
            });
        });
    }
});

