import { Component } from '@angular/core';
import { NavController, Platform } from 'ionic-angular';
import { CameraPreview, CameraPreviewOptions, CameraPreviewPictureOptions } from '@ionic-native/camera-preview';
import { DetectorService } from '../../services/rest/detectorService';

@Component({
  selector: 'page-home',
  templateUrl: 'home.html'
})
export class HomePage {

  constructor(public navCtrl: NavController, public platform: Platform, public cameraPreview: CameraPreview, public detectorService:DetectorService) {
    this.platform.ready().then(() => {
      var width = 0;
      var height = 0;
      if (this.platform.is('ios')) {
        width = window.screen.height;
        height = window.screen.width;
      }
      else if(this.platform.is('android')) {
        width = window.screen.width;
        height = window.screen.height;
      }
      const cameraPreviewOpts: CameraPreviewOptions = {
        x: 0,
        y: 0,
        width: width,
        height: height,
        camera: 'rear',
        tapPhoto: true,
        previewDrag: true,
        toBack: false,
        alpha: 1
      };
      console.log(window.screen.width+"x"+window.screen.height+"-"+window.pageYOffset);
      this.cameraPreview.startCamera(cameraPreviewOpts);
      console.log('HomePage startCamera');
      this.takePicture(detectorService)

    });

  }

  takePicture(detectorService) {
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
        const option: CameraPreviewPictureOptions = {quality: 20};
        this.cameraPreview.setFlashMode("off");
        this.cameraPreview.takePicture(function (imgData) {
          console.log('HomePage takePicture');
          console.log(imgData);
        });
        const bytes: string = atob(imgData);
        const byteNumbers = new Array(bytes.length);
        for (let i = 0; i < bytes.length; i++) {
          byteNumbers[i] = bytes.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);

        const blob: Blob = new Blob([byteArray], { type: 'image/png' });
        detectorService.detector(blob);
      });

    });
  }

}
