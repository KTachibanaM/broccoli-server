import React, { Component } from 'react';
import getDisplayName from "./getDisplayName"
import SchedulerClient from "../clients/SchedulerClient";

export default OriginalComponent => {
  class NewComponent extends Component {
    constructor(props) {
      super(props);
      this.schedulerClient = new SchedulerClient(
        process.env.REACT_APP_SERVER_HOSTNAME,
        parseInt(process.env.REACT_APP_SERVER_PORT),
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
      this.schedulerClient.auth(username, password)
        .then()
    }

    render() {
      if (!this.schedulerClient.hasAuth()) {
        return (
          <div>
            <b>Worker manager: Log in</b>
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
      return (<OriginalComponent schedulerClient={this.schedulerClient} {...this.props} />)
    }
  }

  NewComponent.displayName = `applyWorkerManagerAuth(${getDisplayName(OriginalComponent)})`;
  return NewComponent
}
