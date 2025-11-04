import angular from 'angular';

angular.module('chatApp')
    .component('loginWidget', {
        templateUrl: '/src/login/login.html',
        controller: 'LoginController'
    });

