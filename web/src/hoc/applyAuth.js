import React, { Component } from 'react';
import getDisplayName from "./getDisplayName"
import ApiClient from "../ApiClient";

export default OriginalComponent => {
  class NewComponent extends Component {
    constructor(props) {
      super(props);
      this.apiClient = new ApiClient();
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
      this.apiClient.auth(username, password)
        .then()
    }

    render() {
      if (!this.apiClient.hasAuth()) {
        return (
          <div>
            <b>Log in</b>
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
      return (<OriginalComponent apiClient={this.apiClient} {...this.props} />)
    }
  }

  NewComponent.displayName = `applyApiAuth(${getDisplayName(OriginalComponent)})`;
  return NewComponent
}
