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

#include "PutConfigurationApi.h"

#include "constants.hpp"

#include "spdlog/spdlog.h"

namespace io {
namespace swagger {
namespace server {
namespace api {

using namespace io::swagger::server::model;

PutConfigurationApi::PutConfigurationApi(Pistache::Address addr)
    : httpEndpoint(std::make_shared<Pistache::Http::Endpoint>(addr))
{}

void PutConfigurationApi::init(size_t thr = 2) {
    auto opts = Pistache::Http::Endpoint::options()
        .threads(thr);
    httpEndpoint->init(opts);
    setupRoutes();
}

void PutConfigurationApi::start() {
    httpEndpoint->setHandler(router.handler());
    httpEndpoint->serve();
}

void PutConfigurationApi::shutdown() {
    httpEndpoint->shutdown();
}

void PutConfigurationApi::setupRoutes() {
    using namespace Pistache::Rest;

    Routes::Put(router, irods::rest::base_url + "/put_configuration", Routes::bind(&PutConfigurationApi::handler, this));

    // Default handler, called when a route is not found
    router.addCustomHandler(Routes::bind(&PutConfigurationApi::default_handler, this));
}

void PutConfigurationApi::handler(const Pistache::Rest::Request& request,
                                  Pistache::Http::ResponseWriter response)
{
    try {
        this->handler_impl(request, response);
    }
    catch (const std::runtime_error& e) {
        response.send(Pistache::Http::Code::Bad_Request, e.what());
    }
}

void PutConfigurationApi::default_handler(const Pistache::Rest::Request& request,
                                          Pistache::Http::ResponseWriter response)
{
    response.send(Pistache::Http::Code::Not_Found, "The requested put_configuration method does not exist");
}

}
}
}
}

