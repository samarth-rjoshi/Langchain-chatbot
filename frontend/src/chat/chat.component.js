import angular from 'angular';

angular.module('chatApp')
    .component('chatWidget', {
        templateUrl: '/src/chat/chat.html',
        controller: 'ChatController'
    });


