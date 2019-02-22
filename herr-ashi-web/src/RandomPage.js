import React, {Component} from 'react';
import {Container, Grid, Input, Button} from 'semantic-ui-react'
import ImageRow from './ImageRow'

export default class RandomPage extends Component {
  constructor(props) {
    super(props);
    this.apiClient = this.props.apiClient;
    this.columnCount = this.props.columnCount;

    this.state = {
      "running": false,
      "intervalMilliseconds": 1000,
      "data": [],
      "intervalId": undefined
    };

    this.everyInterval = this.everyInterval.bind(this)
  }

  componentWillUnmount() {
    this.stopInterval()
  }

  start() {
    this.everyInterval();
    this.setState({
      "running": true,
      "intervalId": setInterval(this.everyInterval, this.state.intervalMilliseconds)
    });
  }

  everyInterval() {
    const newImages = Math.max(this.columnCount - this.state.data.length, 1);
    const promises = [];
    for (let i = 0; i < newImages; ++i) {
      promises.push(this.apiClient.random())
    }
    Promise.all(promises)
      .then(data => {
        let newData = [...this.state.data];
        for (let i = 0; i < newImages; ++i) {
          newData.shift()
        }
        newData = newData.concat(data);

        this.setState({
          "data": newData
        })
      })
  }

  stopInterval() {
    if (this.state.intervalId) {
      clearInterval(this.state.intervalId)
    }
  }

  stop() {
    this.stopInterval();
    this.setState({
      "running": false,
      "intervalId": undefined
    });
  }

  render() {
    return (
      <Container>
        <Button
          color={this.state.running ? "red" : "green"}
          onClick={() => {
            if (this.state.running) {
              this.stop()
            } else {
              this.start()
            }
          }}
        >{this.state.running ? "Stop" : "Start"}</Button>
        <Input
          placeholder="Interval (milliseconds)"
          type="number"
          value={this.state.intervalMilliseconds}
          onChange={e => {
            this.setState({
              "intervalMilliseconds": parseInt(e.target.value)
            })
          }}
          disabled={this.state.running}
        />
        <Grid>
          <ImageRow
            columnCount={this.columnCount}
            items={this.state.data}
            rowKey={0}
          />
        </Grid>
      </Container>
    )
  }
}
