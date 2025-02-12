/**
* iRODS REST API
* This is the iRODS REST API
*
* OpenAPI spec version: 1.0.0
* Contact: info@irods.org
*
* NOTE: This class is auto generated by the swagger code generator program.
* https://github.com/swagger-api/swagger-codegen.git
* Do not edit the class manually.
*/

#include "GetConfigurationApi.h"

#include "constants.hpp"

#include "spdlog/spdlog.h"

namespace io {
namespace swagger {
namespace server {
namespace api {

using namespace io::swagger::server::model;

GetConfigurationApi::GetConfigurationApi(Pistache::Address addr)
    : httpEndpoint(std::make_shared<Pistache::Http::Endpoint>(addr))
{ };

void GetConfigurationApi::init(size_t thr = 2) {
    auto opts = Pistache::Http::Endpoint::options()
        .threads(thr);
    httpEndpoint->init(opts);
    setupRoutes();
}

void GetConfigurationApi::start() {
    httpEndpoint->setHandler(router.handler());
    httpEndpoint->serve();
}

void GetConfigurationApi::shutdown() {
    httpEndpoint->shutdown();
}

void GetConfigurationApi::setupRoutes() {
    using namespace Pistache::Rest;

    Routes::Get(router, irods::rest::base_url + "/get_configuration", Routes::bind(&GetConfigurationApi::handler, this));

    // Default handler, called when a route is not found
    router.addCustomHandler(Routes::bind(&GetConfigurationApi::default_handler, this));
}

void GetConfigurationApi::handler(const Pistache::Rest::Request& request,
                                  Pistache::Http::ResponseWriter response)
{
    try {
        this->handler_impl(request, response);
    }
    catch (const std::runtime_error& e) {
        response.send(Pistache::Http::Code::Bad_Request, e.what());
    }
}

void GetConfigurationApi::default_handler(const Pistache::Rest::Request& request,
                                          Pistache::Http::ResponseWriter response)
{
    response.send(Pistache::Http::Code::Not_Found, "The requested get_configuration method does not exist");
}

}
}
}
}

