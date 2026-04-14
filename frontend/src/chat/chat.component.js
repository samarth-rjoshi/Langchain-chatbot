define(['app', 'chat/chat.controller'], function (app) {

    app.component('chatWidget', {
        templateUrl: '/src/chat/chat.html',
        controller: 'ChatController'
    });

});
