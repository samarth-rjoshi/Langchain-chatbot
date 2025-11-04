import angular from 'angular';

angular.module('chatApp')
    .service('ChatService', ['$http', function($http) {
        const API_BASE_URL = 'http://localhost:8000';

        this.sendMessage = function(message) {
            return $http.post(`${API_BASE_URL}/chat`, { message: message }, {
                withCredentials: true
            });
        };
    }]);

