import angular from 'angular';

angular.module('chatApp')
    .service('AuthService', ['$http', '$q', function($http, $q) {
        const API_BASE_URL = 'http://localhost:8000';
        
        let currentUser = null;
        let isAuthenticated = false;

        this.login = function(username, password) {
            return $http.post(`${API_BASE_URL}/login`, { 
                username: username, 
                password: password 
            }, {
                withCredentials: true
            }).then(function(response) {
                if (response.data.status === 'success') {
                    currentUser = response.data.username;
                    isAuthenticated = true;
                    return response.data;
                }
                return $q.reject(response.data);
            });
        };

        this.logout = function() {
            return $http.post(`${API_BASE_URL}/logout`, {}, {
                withCredentials: true
            }).then(function(response) {
                currentUser = null;
                isAuthenticated = false;
                return response.data;
            });
        };

        this.checkAuth = function() {
            return $http.get(`${API_BASE_URL}/check-auth`, {
                withCredentials: true
            }).then(function(response) {
                if (response.data.authenticated) {
                    currentUser = response.data.username;
                    isAuthenticated = true;
                } else {
                    currentUser = null;
                    isAuthenticated = false;
                }
                return response.data;
            });
        };

        this.isAuthenticated = function() {
            return isAuthenticated;
        };

        this.getCurrentUser = function() {
            return currentUser;
        };
    }]);

