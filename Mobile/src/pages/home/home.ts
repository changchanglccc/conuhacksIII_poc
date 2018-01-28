import { Component } from '@angular/core';
import { NavController, Platform } from 'ionic-angular';
import { CameraPreview, CameraPreviewOptions } from '@ionic-native/camera-preview';

@Component({
  selector: 'page-home',
  templateUrl: 'home.html'
})
export class HomePage {

  constructor(public navCtrl: NavController, public platform: Platform, public cameraPreview: CameraPreview) {
    this.platform.ready().then(() => {
      const cameraPreviewOpts: CameraPreviewOptions = {
        x: 0,
        y: 0,
        width: window.screen.width,
        height: window.screen.height,
        camera: 'rear',
        tapPhoto: true,
        previewDrag: true,
        toBack: false,
        alpha: 1
      };
      console.log(window.screen.width+"x"+window.screen.height);
      this.cameraPreview.startCamera(cameraPreviewOpts);
      console.log('HomePage startCamera');
      // this.cameraPreview.takePicture(function(imgData){
      //   console.log('HomePage takePicture');
      //   console.log(imgData);
      // });

    });

  }

  startCameraAbove() {
    console.log('Begin startCamera');
    this.platform.ready().then(() => {
      // const cameraPreviewOpts: CameraPreviewOptions = {
      //   x: 0,
      //   y: 0,
      //   width: window.screen.width,
      //   height: window.screen.height,
      //   camera: 'rear',
      //   tapPhoto: true,
      //   previewDrag: true,
      //   toBack: false,
      //   alpha: 1
      // };
      // console.log(window.screen.width+"x"+window.screen.height);
      // this.cameraPreview.startCamera(cameraPreviewOpts);
      // console.log('HomePage startCamera');
      this.cameraPreview.takePicture(function(imgData){
        console.log('HomePage takePicture');
        console.log(imgData);
      });

    });
  }

}
