#include "guest.h"
#include "sql_guest.h"
#include "receiver.h"
#include <AMQPcpp.h>
#include <boost/foreach.hpp>
#include <json/json.h>
#include <sstream>

int main() {
    Receiver receiver("guest:guest@localhost:5672/", "guest.hostname", "%");
    MySqlGuestPtr guest(new MySqlGuest());
    MySqlMessageHandler handler(guest);

#ifndef _DEBUG
    try {
        daemon(1,0);
#endif
        while(true) {
            syslog(LOG_INFO, "getting and getting");
            json_object * new_obj = receiver.next_message();
            syslog(LOG_INFO, "output of json %s",
                   json_object_to_json_string(new_obj));
            handler.handle_message(new_obj);
            receiver.finish_message(new_obj);
        }
#ifndef _DEBUG
    } catch (AMQPException e) {
        syslog(LOG_ERR,"Exception! Code %i, message = %s",
               e.getReplyCode(),
               e.getMessage().c_str());
    }
#endif
    return 0;
}
