define(['app', 'login/login.controller'], function (app) {

    app.component('loginWidget', {
        templateUrl: '/src/login/login.html',
        controller: 'LoginController'
    });

});
