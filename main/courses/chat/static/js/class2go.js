var CandyShop = (function(self) { return self; }(CandyShop || {}));

CandyShop.Class2Go = (function(self, Candy, $) {
    //var _numColors;

    self.init = function() {
        Candy.View.Event.Room.onAdd = function(roomPane) {
            var roomType = roomPane['type'];
            var roomTabClass;
            if (roomType === 'groupchat') {
                roomTabClass = 'icon-group';
            } else {
                roomTabClass = 'icon-user';
            }
            var roomTab = $('#chat-tabs li').attr('data-roomjid', roomPane['roomJid']).find('.label');
            
            roomTab.addClass(roomTabClass).attr('title', roomTab.text()).html('');
        }
        
        Candy.View.Event.Roster.onUpdate = function(rosterUser) {
            var currentUser = $('#chat-rooms .room-pane .roster-pane .user').attr('data-jid', rosterUser['user']['data']['jid']);
            var userIcon;
            if (currentUser.hasClass('me')) {
                userIcon = 'icon-flag';
            }
            currentUser.find('.label').html('<em class="' + userIcon + '"></em> ' + currentUser.find('.label').text());
        }
    };

    return self;
}(CandyShop.Class2Go || {}, Candy, jQuery));