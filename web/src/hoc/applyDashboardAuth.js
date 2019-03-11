import React, { Component } from 'react';
import getDisplayName from "./getDisplayName"
import DashboardClient from "../clients/DashboardClient";

export default OriginalComponent => {
  class NewComponent extends Component {
    constructor(props) {
      super(props);
      this.dashboardClient = new DashboardClient(
        process.env.REACT_APP_SERVER_HOSTNAME,
        parseInt(process.env.REACT_APP_SERVER_PORT)
      );
      this.state = {
        "username": "",
        "password": ""
      };

      this.onSubmit = this.onSubmit.bind(this);
    }

    onSubmit(e) {
      this.submit();
      e.preventDefault()
    }

    submit() {
      const {
        username,
        password
      } = this.state;
      this.dashboardClient.auth(username, password)
        .then()
    }

    render() {
      if (!this.dashboardClient.hasAuth()) {
        return (
          <div>
            <b>API: Log in</b>
            <div>
              Username:<br/>
              <input
                type="text"
                value={this.state.username}
                onChange={e => {this.setState({"username": e.target.value})}}
              /><br/>
              Password:<br/>
              <input
                type="password"
                value={this.state.password}
                onChange={e => {this.setState({"password": e.target.value})}}
              /><br/>
              <button onClick={this.onSubmit}>Submit</button>
            </div>
          </div>
        )
      }
      return (<OriginalComponent dashboardClient={this.dashboardClient} {...this.props} />)
    }
  }

  NewComponent.displayName = `applyApiAuth(${getDisplayName(OriginalComponent)})`;
  return NewComponent
}
